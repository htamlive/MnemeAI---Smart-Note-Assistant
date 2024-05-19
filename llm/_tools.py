from datetime import datetime, timezone, timedelta
from typing import List

import pytz
from telegram import InlineKeyboardMarkup

from bot.telegram.ui_templates import (
    get_note_option_keyboard,
    get_reminder_option_keyboard,
    render_html_note_detail,
    render_html_reminder_detail,
    show_notes_list_template,
    show_reminders_list_v2 as show_reminders_list,
)
from config.config import TELEGRAM_SEND_ENDPOINT
from llm.models import UserData
from pkg.google_calendar_api.client import GoogleCalendarApi
from pkg.google_task_api.client import GoogleTaskClient
from pkg.google_task_api.model import ListTask, Task
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.celery import send_notification
from django.utils import timezone as dj_timezone

import requests
from pkg.notion_api.client import NotionClient

from asgiref.sync import sync_to_async

from pkg.notion_api.model import ListNotes, Notes


async def check_google_calendar_auth(
    user_data: UserData, google_task_client: GoogleTaskClient = GoogleTaskClient()
) -> bool:
    chat_id = user_data.chat_id
    if google_task_client is None:
        google_task_client = GoogleTaskClient()
    return await sync_to_async(google_task_client.check_auth)(chat_id)

async def check_notion_auth(
    user_data: UserData, client: NotionClient = NotionClient()
) -> bool:
    chat_id = user_data.chat_id
    return await sync_to_async(client.check_auth)(chat_id) and (await sync_to_async(client.get_database_id)(chat_id) is not None)


async def update_timezone_utc(user_data: UserData, offset: int = 0) -> str:
    if offset == 0:
        user_data.timezone = pytz.timezone("Etc/GMT")
    else:
        if offset > 0:
            user_data.timezone = pytz.timezone(f"Etc/GMT-{abs(offset)}")
        else:
            user_data.timezone = pytz.timezone(f"Etc/GMT+{abs(offset)}")

    current_time = datetime.now(user_data.timezone)
    return f"Timezone updated to UTC{offset:+d} and current time is {current_time.strftime('%H:%M %A %d %B %Y')}"


async def create_task(
    user_data: UserData,
    title: str,
    body: str,
    due,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    timezone = user_data.timezone.zone
    # Save the reminder by calling the Google Task API
    event = Task(title=title, notes=body, due=due, timezone=timezone)
    google_task_client = GoogleCalendarApi()
    result = await sync_to_async(google_task_client.insert_task)(chat_id, event)
    if result is None:
        return "Event cannot be created"
    # Inserting the Celery task
    await sync_to_async(ReminderCeleryTask.objects.create)(
        title=title,
        description=body,
        chat_id=chat_id,
        reminder_id=result.id,
        due=datetime.fromisoformat(result.start),
        timezone=timezone,
        state=ReminderCeleryTask.PENDING,
    )
    # Setting up the Celery task
    timezone_info = pytz.timezone(timezone)
    countdown = datetime.fromisoformat(result.start) - datetime.now(timezone_info)
    countdown_sec_round_down = max(countdown.total_seconds() // 60, 1) * 60
    await sync_to_async(send_notification.apply_async)(
        args=(chat_id, result.id),
        countdown=countdown_sec_round_down,
        expires=countdown_sec_round_down + 5 * 60,
    )
    return f"Created task: {title}, Body: {body}, Due: {due}"


async def show_task_detail(
    user_data: UserData, google_task_client: GoogleCalendarApi | None = None
):

    task_token = user_data.reminder_token
    chat_id = user_data.chat_id

    if chat_id is None:
        return "Error: Cannot show the detail."

    if task_token is None:
        return "Error: User needs to select tasks from the list"

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    if not await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    ):
        return "Error: Not authorized to create a task."

    task = await sync_to_async(google_task_client.get_task)(
        chat_id=chat_id, task_id=task_token
    )
    if task is None:
        return "Error: Task not found."

    title, detail = task.title, task.notes

    start_reminding_time = dj_timezone.localtime(task.start).strftime(
        "Due time: %H:%M %A %d %B %Y"
    )

    endpoint = TELEGRAM_SEND_ENDPOINT

    payload = {
        "chat_id": chat_id,
        "text": render_html_reminder_detail(start_reminding_time, title, detail),
        "parse_mode": "HTML",
        "reply_markup": InlineKeyboardMarkup(
            get_reminder_option_keyboard(task_token)
        ).to_json(),
    }

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Error: Cannot show the task detail."

    return "Task shown successfully."


async def show_task_list(
    user_data: UserData, google_task_client: GoogleCalendarApi | None = None
) -> str:
    chat_id = user_data.chat_id
    timezone = user_data.timezone.zone

    if chat_id is None:
        return "Error: Cannot show the list."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    if not await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    ):
        return "Error: Not authorized to create a task."

    tasks: ListTask = await sync_to_async(google_task_client.list_tasks)(
        chat_id=chat_id,
        timezone=timezone,
    )

    if tasks is None:
        return "Error: Cannot show the list."

    titles = [task.title for task in tasks.items]
    reminder_tokens = [task.id for task in tasks.items]

    next_page_token = tasks.nextPageToken

    endpoint = TELEGRAM_SEND_ENDPOINT

    payload = show_reminders_list(chat_id, titles, reminder_tokens, next_page_token)
    payload["parse_mode"] = "HTML"
    payload["reply_markup"] = payload["reply_markup"].to_json()

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Error: Cannot show the list."

    return "List has been shown. Let some time for the user to see the list."


async def save_task_title(
    user_data: UserData,
    title_text: str,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if reminder_token is None or chat_id is None:
        return "Error: Cannot save the title."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    event: Task = await sync_to_async(google_task_client.get_task)(
        chat_id=chat_id, task_id=reminder_token
    )
    print("Task:", event)
    event.title = title_text

    if user_data.timezone is not None:
        event.timezone = user_data.timezone.zone

    await sync_to_async(google_task_client.update_task)(
        chat_id=chat_id, task_id=reminder_token, task=event
    )
    return f"Title saved: {title_text}"


async def save_task_detail(
    user_data: UserData,
    detail_text: str,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if reminder_token is None or chat_id is None:
        return "Error: Cannot save the detail."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    event: Task = await sync_to_async(google_task_client.get_task)(
        chat_id=chat_id, task_id=reminder_token
    )
    event.notes = detail_text

    if user_data.timezone is not None:
        event.timezone = user_data.timezone.zone

    await sync_to_async(google_task_client.update_task)(
        chat_id=chat_id, task_id=reminder_token, task=event
    )
    return f"Detail saved: {detail_text}"


async def save_task_time(
    user_data: UserData,
    time: str,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if reminder_token is None or chat_id is None:
        return "Error: Cannot save the time."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    event: Task = await sync_to_async(google_task_client.get_task)(
        chat_id=chat_id, task_id=reminder_token
    )

    await delete_task(
        user_data, task_name=event.title, google_task_client=google_task_client
    )

    await create_task(
        user_data,
        event.title,
        event.notes,
        time,
        google_task_client=google_task_client,
    )
    return f"Time saved: {time}"


async def delete_task(
    user_data: UserData,
    task_name: str | None = None,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_calendar_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    token = user_data.reminder_token

    if token is None or chat_id is None:
        return "Error: Cannot delete the task."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    await sync_to_async(google_task_client.delete_task)(
        chat_id=chat_id,
        task_id=token,
    )
    # Cancel the Celery task
    reminder = await sync_to_async(ReminderCeleryTask.objects.filter)(
        chat_id=chat_id,
        reminder_id=token,
        completed=False,
    )
    await sync_to_async(reminder.update)(state=ReminderCeleryTask.REVOKED)

    return f"Deleted task: {task_name}"


async def create_notes(
    user_data: UserData, title: str, content: str, client: NotionClient | None = None
) -> str:
    chat_id = user_data.chat_id

    if client is None:
        client = NotionClient()

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to create a note."

    resp = await sync_to_async(client.post_notes)(chat_id, title, content)

    return f"Added note: {title}, Note: {content}"


async def save_notes_title(
    user_data: UserData, title: str, client: NotionClient = NotionClient()
) -> str:

    return await update_note(user_data, title=title, client=client)


async def save_notes_detail(
    user_data: UserData, content: str, client: NotionClient = NotionClient()
) -> str:

    return await update_note(user_data, content=content, client=client)


async def update_note(
    user_data: UserData,
    title: str = None,
    content: str = None,
    client: NotionClient = NotionClient(),
) -> str:
    chat_id = user_data.chat_id
    note_id = user_data.note_token

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to update a note."

    try:
        resp = await sync_to_async(client.patch_notes)(chat_id, note_id, title, content)
    except Exception as e:
        return f"Cannot update this. Please view the latest notes."

    return f"note is updated"


async def show_notes_detail(
    user_data: UserData, client: NotionClient = NotionClient()
) -> str:
    note_id = user_data.note_token
    chat_id = user_data.chat_id

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to view a note."

    try:
        notes = await sync_to_async(client.get_notes)(chat_id, note_id)
    except Exception as e:
        return f"Cannot view this. Ask the user to view the latest notes."

    endpoint = TELEGRAM_SEND_ENDPOINT

    payload = {
        "chat_id": chat_id,
        "text": render_html_note_detail(notes.title, notes.notes),
        "parse_mode": "HTML",
    } | (
        {"reply_markup": InlineKeyboardMarkup(get_note_option_keyboard(note_id))}
        if not notes.deleted
        else {}
    )
    payload["parse_mode"] = "HTML"
    payload["reply_markup"] = payload["reply_markup"].to_json()

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Note detail cannot be shown. Ask the user to view the latest notes."

    return f"Show note sucessfully"


async def show_notes_list(
    user_data: UserData,
    client: NotionClient = NotionClient(),
    starting_point: str | None = None,
) -> str:
    chat_id = user_data.chat_id

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to view a note."

    list_notes: ListNotes = await sync_to_async(client.get_notes_list)(
        chat_id, starting_point
    )

    titles = []
    notes_tokens = []

    for q in list_notes.data:
        token = q["id"]
        title = q["title"]

        notes_tokens.append(token)
        titles.append(title)

    endpoint = TELEGRAM_SEND_ENDPOINT

    next_page_token = list_notes.startingPoint

    payload = show_notes_list_template(chat_id, titles, notes_tokens, next_page_token)
    payload["parse_mode"] = "HTML"
    payload["reply_markup"] = payload["reply_markup"].to_json()

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Error: Cannot show the list."

    return "User has been shown the list. Ask the user what to do next."


async def delete_notes(
    user_data: UserData, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id
    note_id = user_data.note_token

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to delete a note."

    notes: Notes = await sync_to_async(client.get_notes)(chat_id, note_id)

    title = notes.title
    # content = "".join([string['rich_text'] for string in props['Description']['rich_text']])

    await sync_to_async(client.delete_notes)(chat_id, note_id)

    return f"Note {title} is deleted"


async def delete_all_notes(
    user_data: UserData, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to delete a note."

    await sync_to_async(client.delete_all_notes)(chat_id)

    return "Deleted all notes"


async def register_database_id(
    user_data: UserData, database_id: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id
    type = client.check_type(chat_id, database_id)

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to register a database."

    if type == "database":
        resp = await sync_to_async(client.register_database_id)(chat_id, database_id)

        return f"Registered database {database_id} to user {chat_id}"
    elif type == "page":
        page_id = database_id
        resp = await sync_to_async(client.register_page_database)(chat_id, page_id)

        return f"Registered database {resp['id']} in page {page_id} to user {chat_id}"
    else:
        return f"This is a {type} object, try again"


# async def register_page_database(user_data: UserData, page_id: str, client: NotionClient = NotionClient()) -> str:
#     chat_id = user_data.chat_id
#     type = client.check_type(chat_id, page_id)
#     if type != "page":
#         pass
#     resp = await sync_to_async(client.register_page_database)(chat_id, page_id)

#     return f"Registered database {resp['id']} in page {page_id} to user {chat_id}"


async def check_type(
    user_data: UserData, content_id: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id

    resp = await sync_to_async(client.check_type)(chat_id, content_id)

    return resp


async def retrieve_knowledge_from_notes(
    user_data: UserData, prompt, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id

    if not await check_notion_auth(user_data, client=client):
        return "Error: Not authorized to retrieve knowledge from notes."

    json_obj = await sync_to_async(client.query)(chat_id, prompt)

    print(json_obj)
    if json_obj is None:
        return "There is some error in retrieving the content"

    choices = json_obj["choices"]

    content = "\n\n".join(map(lambda x: x["message"]["content"], choices))

    endpoint = TELEGRAM_SEND_ENDPOINT

    payload = {
        "chat_id": chat_id,
        "text": content,
        "parse_mode": "Markdown",
    }

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Error: Cannot show the content."

    return "Content has been retrieved"
