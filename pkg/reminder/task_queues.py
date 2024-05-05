from celery import Celery

app = Celery('reminder', broker='redis://localhost:6379/0')

@app.task
def queue_task(chat_id: str, id: int):
    
    return f"Task queued: {chat_id} - {id}"
