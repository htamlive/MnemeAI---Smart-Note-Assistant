from datetime import datetime, timezone, timedelta
from typing import List

from llm.models import UserData
from pkg.google_task_api.client import GoogleTaskClient
from pkg.google_task_api.model import Task
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.celery import send_notification

from asgiref.sync import sync_to_async


async def create_task(user_data: UserData, title: str, body: str, due, google_task_client: GoogleTaskClient | None = None) -> str:
    # Save the reminder by calling the Google Task API
    
    chat_id = user_data.chat_id
    map_datetime = datetime.strptime(due, "%Y-%m-%d %H:%M")
    task = Task(
        title=title,
        notes=body,
        due=map_datetime.replace(tzinfo=timezone.utc).isoformat(),
    )
    # print("Task:", task)

    if google_task_client is None:
        google_task_client = GoogleTaskClient()
    result = await sync_to_async(google_task_client.insert_task)(chat_id, task)
    if result is None:
        return "Task cannot be created"
    # format datetime as timestamptz
    formatted_datetime = map_datetime.strftime("%Y-%m-%d %H:%M:%S%z")
    await sync_to_async(ReminderCeleryTask.objects.create)(
        title=title,
        description=body,
        chat_id=chat_id,
        reminder_id=result.id,
        due=formatted_datetime,
        state=ReminderCeleryTask.PENDING,
    )
    # Setting up the Celery task
    send_notification.apply_async(
        args=(chat_id, result.id),
        countdown=(map_datetime - datetime.now()).total_seconds(),
        expires=map_datetime + timedelta(minutes=5),
    )
    return f"Created task: {title}, Body: {body}, Due: {datetime}"

async def save_task_title(user_data: UserData, title_text: str, google_task_client: GoogleTaskClient | None = None) -> str:
    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if reminder_token is None or chat_id is None:
        return "Error: Cannot save the title."
    
    if google_task_client is None:
        google_task_client = GoogleTaskClient()

    task : Task = await sync_to_async(google_task_client.get_task)(chat_id=chat_id, task_id=reminder_token)
    print("Task:", task)

    task.title = title_text
    await sync_to_async(google_task_client.update_task)(chat_id=chat_id, task_id=reminder_token, task=task)
    return f"Title saved: {title_text}"

async def save_task_detail(user_data: UserData, detail_text: str, google_task_client: GoogleTaskClient | None = None) -> str:
    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if(reminder_token is None or chat_id is None):
        return "Error: Cannot save the detail."
    
    if google_task_client is None:
        google_task_client = GoogleTaskClient()

    task : Task = await sync_to_async(google_task_client.get_task)(chat_id=chat_id, task_id=reminder_token)
    task.notes = detail_text
    await sync_to_async(google_task_client.update_task)(chat_id=chat_id, task_id=reminder_token, task=task)
    return f"Detail saved: {detail_text}"

async def save_task_time(user_data: UserData, time: datetime, google_task_client: GoogleTaskClient | None = None) -> str:
    chat_id = user_data.chat_id
    reminder_token = user_data.reminder_token

    if reminder_token is None or chat_id is None:
        return "Error: Cannot save the time."
    
    if google_task_client is None:
        google_task_client = GoogleTaskClient()
    
    task : Task = await sync_to_async(google_task_client.get_task)(chat_id=chat_id, task_id=reminder_token)

    await delete_task(user_data, google_task_client=google_task_client)
    await sync_to_async(google_task_client.delete_task)(chat_id=chat_id, task_id=reminder_token)

    await create_task(user_data, task.title, task.notes, time, google_task_client=google_task_client)
    return f"Time saved: {time}"


async def delete_task(user_data: UserData, task_name: str | None = None, google_task_client: GoogleTaskClient | None = None) -> str:
    chat_id = user_data.chat_id
    token = user_data.reminder_token

    if token is None or chat_id is None:
        return "Error: Cannot delete the task."

    if google_task_client is None:
        google_task_client = GoogleTaskClient()


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


async def add_note(chat_id: int, title: str, content: str) -> str:
    return f"Added note: {title}, Note: {content}"


async def get_note(chat_id: int, queries_str: str) -> List[str]:
    return ["Building a rocket", "fighting a mummy", "climbing up the Eiffel Tower"]
