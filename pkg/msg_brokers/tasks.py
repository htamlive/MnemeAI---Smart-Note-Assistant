import os
import dotenv
import requests
from pkg.model.reminder_cele_task import ReminderCeleryTask
from .celery import app


@app.task(
    autoretry_for=(requests.HTTPError,),
    retry_kwargs={"max_retries": 5},
    default_retry_delay=60, # 1 minute
)
def send_notification(
    endpoint: str,
    chat_id: int,
    idx: int,
):
    try:
        reminder_celery = ReminderCeleryTask.objects.get(chat_id=chat_id, id=idx)
        # Check if the task has been cancelled
        if reminder_celery.is_cancelled():
            print(f"Reminder {chat_id} - {idx} has been cancelled")
            return
        # Send the notification to the user
        payload = {
            "chat_id": chat_id,
            "text": "Hey, remember to do this task: " + reminder_celery.title,
        }
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        # Mark the task as completed
        reminder_celery.mark_completed()
        reminder_celery.save()
    except ReminderCeleryTask.DoesNotExist as e:
        print(f"Reminder {chat_id} - {idx} does not exist:\n{e}")
