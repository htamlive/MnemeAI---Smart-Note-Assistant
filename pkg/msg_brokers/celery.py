from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0")

# To run the worker:
# celery -A pkg.msg_brokers worker -l INFO