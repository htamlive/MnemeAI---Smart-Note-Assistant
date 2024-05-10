import os
from celery import Celery
import requests
import dotenv

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
    dotenv.load_dotenv()
    reminder = ReminderCeleryTask.objects.get(
        chat_id=chat_id, reminder_id=idx
    )
    if reminder.is_cancelled():
        return
    telebot_token = os.getenv("TELEBOT_TOKEN")
    endpoint = f"https://api.telegram.org/bot{telebot_token}/sendMessage"
    print (reminder.title)
    payload = {
        "chat_id": chat_id,
        "text": "Hey, remember to do this task: " + reminder.title,
    }
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    ReminderCeleryTask.objects.filter(
        chat_id = chat_id,
        reminder_id = idx
    ).update(completed = True)


# To run the worker:
# celery -A pkg.msg_brokers worker -l INFO
