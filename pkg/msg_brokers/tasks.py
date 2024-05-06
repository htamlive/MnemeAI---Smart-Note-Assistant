from pkg.model.reminder_cele_task import ReminderCeleryTask
from .celery import app

@app.task
def send_notification(
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
        print(f"Sending notification to {chat_id} - {idx}")

        # Mark the task as completed
        reminder_celery.mark_completed()
        reminder_celery.save()
    except ReminderCeleryTask.DoesNotExist as e:
        print(f"Reminder {chat_id} - {idx} does not exist")
