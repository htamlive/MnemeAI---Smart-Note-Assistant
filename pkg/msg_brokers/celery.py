from celery import Celery
import requests

from config import config
from pkg.model.reminder_cele_task import ReminderCeleryTask
from .outside_module import render_html_task_notification

app = Celery(
    "tasks", broker=config.REDIS_URL, broker_connection_retry_on_startup=True
)

@app.task(
    autoretry_for=(requests.HTTPError,),
    retry_kwargs={"max_retries": 5},
    default_retry_delay=60,  # 1 minute

)
def send_notification(
    chat_id: int,
    idx: str,
):
    reminder = ReminderCeleryTask.objects.get(chat_id=chat_id, reminder_id=idx)
    if reminder.is_cancelled():
        print("Reminder is cancelled")
        return
    telebot_token = config.TELEBOT_TOKEN
    endpoint = f"https://api.telegram.org/bot{telebot_token}/sendMessage"
    print(reminder.title)
    
    payload = {
        "chat_id": chat_id,
        "text": render_html_task_notification(reminder),
        "parse_mode": "HTML",
    }
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    ReminderCeleryTask.objects.filter(chat_id=chat_id, reminder_id=idx).update(
        completed=True
    )


# To run the worker:
# celery -A pkg.msg_brokers worker -l INFO
