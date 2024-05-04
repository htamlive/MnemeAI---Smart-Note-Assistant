from pkg.google_task_api.client import Client
from pkg.google_task_api.model import Task

if __name__ == '__main__':
    client = Client()
    print(client.insert_task(1,Task(
        # kind='tasks#task',
        title='Test task',
        notes='Test notes')))