from datetime import datetime
from typing import List

from telegram import InlineKeyboardMarkup

from bot.telegram.ui_templates import (
    get_reminder_option_keyboard,
    render_html_reminder_detail,
    show_notes_list,
    show_reminders_list,
)
from config.config import TELEGRAM_SEND_ENDPOINT
from llm.models import UserData
from pkg.google_calendar_api.client import GoogleCalendarApi
from pkg.google_calendar_api.model import CalendarEvent, CalendarEventList
from pkg.google_task_api.model import ListTask, Task
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.celery import send_notification
from django.utils import timezone as dj_timezone

import requests
from pkg.notion_api.client import NotionClient

from asgiref.sync import sync_to_async

from pkg.notion_api.model import ListNotes


async def check_google_task_auth(
    user_data: UserData, google_task_client: GoogleCalendarApi | None = None
) -> bool:
    chat_id = user_data.chat_id
    if google_task_client is None:
        google_task_client = GoogleCalendarApi()
    return await sync_to_async(google_task_client.check_auth)(chat_id)


async def create_task(
    user_data: UserData,
    title: str,
    body: str,
    due,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_task_auth(
        user_data, google_task_client=google_task_client
    )

    if not authorized:
        return "Error: Not authorized to create a task."

    chat_id = user_data.chat_id
    # Save the reminder by calling the Google Task API
    event = Task(
        title=title,
        notes=body,
        due=due,
    )
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
        state=ReminderCeleryTask.PENDING,
    )
    # Setting up the Celery task
    mapped_datetime = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
    await sync_to_async(send_notification.apply_async)(
        args=(chat_id, result.id),
        countdown=(mapped_datetime - datetime.datetime.now()).total_seconds(),
        expires=mapped_datetime + datetime.timedelta(minutes=5),
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

    if not await check_google_task_auth(
        user_data, google_task_client=google_task_client
    ):
        return "Error: Not authorized to create a task."

    task = await sync_to_async(google_task_client.get_task)(
        chat_id=chat_id, task_id=task_token
    )
    if task is None:
        return "Error: Task not found."

    title, detail = task.title, task.notes

    reminder = await sync_to_async(ReminderCeleryTask.objects.get)(
        chat_id=chat_id, reminder_id=task_token
    )

    due = dj_timezone.localtime(reminder.due).strftime("Due time: %H:%M %A %d %B %Y")

    endpoint = TELEGRAM_SEND_ENDPOINT

    payload = {
        "chat_id": chat_id,
        "text": render_html_reminder_detail(due, title, detail),
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

    if chat_id is None:
        return "Error: Cannot show the list."

    if google_task_client is None:
        google_task_client = GoogleCalendarApi()

    if not await check_google_task_auth(
        user_data, google_task_client=google_task_client
    ):
        return "Error: Not authorized to create a task."

    tasks: ListTask = await sync_to_async(google_task_client.list_tasks)(
        chat_id=chat_id
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

    authorized = await check_google_task_auth(
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
    await sync_to_async(google_task_client.update_task)(
        chat_id=chat_id, task_id=reminder_token, task=event
    )
    return f"Title saved: {title_text}"


async def save_task_detail(
    user_data: UserData,
    detail_text: str,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_task_auth(
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
    await sync_to_async(google_task_client.update_task)(
        chat_id=chat_id, task_id=reminder_token, task=event
    )
    return f"Detail saved: {detail_text}"


async def save_task_time(
    user_data: UserData,
    time: datetime,
    google_task_client: GoogleCalendarApi | None = None,
) -> str:

    authorized = await check_google_task_auth(
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
    await sync_to_async(google_task_client.delete_task)(
        chat_id=chat_id, task_id=reminder_token
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

    authorized = await check_google_task_auth(
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


async def add_note(
    user_data: UserData, title: str, content: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id

    resp = await sync_to_async(client.post_notes)(chat_id, title, content)

    return f"Added note: {title}, Note: {content}"


async def update_note(
    user_data: UserData,
    note_id: str,
    title: str = None,
    content: str = None,
    client: NotionClient = NotionClient(),
) -> str:
    chat_id = user_data.chat_id
    note_id = client.extract_notion_id(note_id)
    resp = await sync_to_async(client.patch_notes)(chat_id, note_id, title, content)

    return f"Updated note"


async def get_note_idx(
    user_data: UserData, note_id: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id
    note_id = client.extract_notion_id(note_id)

    resp = await sync_to_async(client.get_notes_idx)(chat_id, note_id)
    props = resp["properties"]

    title = " ".join([string["plain_text"] for string in props["Name"]["title"]])
    content = "".join(
        [string["rich_text"] for string in props["Description"]["rich_text"]]
    )

    return f"Got note: {title}, Note: {content}"


async def get_notes_list(
    user_data: UserData,
    client: NotionClient = NotionClient(),
    starting_point: str | None = None,
) -> str:
    chat_id = user_data.chat_id

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

    payload = show_notes_list(chat_id, titles, notes_tokens, next_page_token)
    payload["parse_mode"] = "HTML"
    payload["reply_markup"] = payload["reply_markup"].to_json()

    response = requests.post(endpoint, json=payload)

    if response.status_code != 200:
        return "Error: Cannot show the list."

    return "List has been shown. Let some time for the user to see the list."


async def delete_notes(
    user_data: UserData, note_id: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id
    note_id = client.extract_notion_id(note_id)

    resp = await sync_to_async(client.get_notes_idx)(chat_id, note_id)
    props = resp["properties"]

    title = " ".join([string["plain_text"] for string in props["Name"]["title"]])
    # content = "".join([string['rich_text'] for string in props['Description']['rich_text']])

    return f"Note {title} is deleted"


async def delete_all_notes(
    user_data: UserData, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id

    await sync_to_async(client.delete_all_notes)(chat_id)

    return "Deleted all notes"


async def register_database_id(
    user_data: UserData, database_id: str, client: NotionClient = NotionClient()
) -> str:
    chat_id = user_data.chat_id
    type = client.check_type(chat_id, database_id)
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
