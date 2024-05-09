import os
from celery import Celery
import requests

from pkg.model.reminder_cele_task import ReminderCeleryTask

app = Celery("tasks", broker="redis://localhost:6379/0")


@app.task(
    autoretry_for=(requests.HTTPError,),
    retry_kwargs={"max_retries": 5},
    default_retry_delay=60,  # 1 minute
)
def send_notification(
    chat_id: int,
    idx: str,
):
    telebot_token = os.getenv("TELEBOT_TOKEN")
    endpoint = f"https://api.telegram.org/bot{telebot_token}/sendMessage"
    # try:
    #     reminder_celery = ReminderCeleryTask.objects.get(chat_id=chat_id, reminder_id=idx)
    #     # Check if the task has been cancelled
    #     if reminder_celery.is_cancelled():
    #         print(f"Reminder {chat_id} - {idx} has been cancelled")
    #         return
    #     # Send the notification to the user
    #     payload = {
    #         "chat_id": chat_id,
    #         "text": "Hey, remember to do this task: " + reminder_celery.title,
    #     }
    #     response = requests.post(endpoint, json=payload)
    #     response.raise_for_status()
    #     # Mark the task as completed
    #     reminder_celery.mark_completed()
    #     reminder_celery.save()
    # except ReminderCeleryTask.DoesNotExist as e:
    #     print(f"Reminder {chat_id} - {idx} does not exist:\n{e}")
    # reminder_celery = ReminderCeleryTask.objects.get(chat_id=chat_id, reminder_id=idx)
    # # Check if the task has been cancelled
    # if reminder_celery.is_cancelled():
    #     print(f"Reminder {chat_id} - {idx} has been cancelled")
    #     return
    # # Send the notification to the user
    payload = {
        "chat_id": chat_id,
        "text": "Hey, remember to do this task: ",  # + reminder_celery.title,
    }
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    # # Mark the task as completed
    # reminder_celery.mark_completed()
    # reminder_celery.save()


# To run the worker:
# celery -A pkg.msg_brokers worker -l INFO
