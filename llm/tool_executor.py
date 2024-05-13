from datetime import timezone, datetime, timedelta
import re
import ast
from typing import List

from pkg.google_task_api.client import GoogleTaskClient
from pkg.google_task_api.model import Task
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.celery import send_notification

from asgiref.sync import sync_to_async

# Define mock functions
async def create_task(chat_id: int, title: str, body: str, due) -> str:
    # Save the reminder by calling the Google Task API
    map_datetime = datetime.strptime(due, "%Y-%m-%d %H:%M")
    task = Task(
        title=title,
        notes=body,
        due=map_datetime.replace(tzinfo=timezone.utc).isoformat(),
    )
    # print("Task:", task)

    google_task_client = GoogleTaskClient()
    result = await sync_to_async(google_task_client.insert_task)(chat_id, task)
    if result is None:
        return "Task cannot be created"
    # Inserting the Celery task
    await sync_to_async(ReminderCeleryTask.objects.create)(
        title=title,
        description=body,
        chat_id=chat_id,
        reminder_id=result.id,
        state=ReminderCeleryTask.PENDING,
    )
    # Setting up the Celery task
    send_notification.apply_async(
        args=(chat_id, result.id),
        countdown=(map_datetime - datetime.now()).total_seconds(),
        expires=map_datetime + timedelta(minutes=5),
    )
    return f"Created task: {title}, Body: {body}, Due: {datetime}"


async def delete_task(chat_id: int, task_name: str) -> str:
    client = GoogleTaskClient()
    tasks = client.list_tasks(chat_id=chat_id)
    to_be_removed_task = None
    if tasks.items is not None:
        to_be_removed_task = filter(
            lambda task: task.title == task_name,
            tasks.items
        )
    if len(to_be_removed_task) == 0:
        return
    to_be_removed_task = to_be_removed_task[0]
    client.delete_task(
        chat_id=chat_id,
        task_id=to_be_removed_task.id,
    )
    # Cancel the Celery task
    reminder = ReminderCeleryTask.objects.filter(
        chat_id=chat_id,
        reminder_id=to_be_removed_task.id,
        completed=False,
    )
    reminder.update(state=ReminderCeleryTask.REVOKED)
    return f"Deleted task: {task_name}"


async def add_note(chat_id: int, title: str, content: str) -> str:
    return f"Added note: {title}, Note: {content}"


async def get_note(chat_id: int, queries_str: str) -> List[str]:
    return ["Building a rocket", "fighting a mummy", "climbing up the Eiffel Tower"]


# @traceable
class ToolExecutor:
    def __init__(self):
        self.function_map: dict[str, callable] = {
            "create_task": create_task,
            "delete_task": delete_task,
            "add_note": add_note,
            "get_note": get_note,
        }

    async def execute_from_string(self, chat_id, raw_str) -> str:
        # Extract function call string using regular expression
        function_call_match = re.search(r"(\w+)\((.*?)\)", raw_str)

        if function_call_match:
            # Extract function name and its arguments
            function_name = function_call_match.group(1)
            arguments_str = function_call_match.group(2)

            # Parse arguments string into a Python literal
            try:
                arguments = ast.literal_eval(arguments_str)

                # If the argument is a single value, convert it to a tuple
                if not isinstance(arguments, tuple):
                    arguments = (arguments,)

                arguments = (chat_id,) + arguments
            except (SyntaxError, ValueError):
                return "Error: Failed to parse arguments string."

            # Check if function exists
            if function_name in self.function_map:
                # Execute the function call
                return await self.function_map[function_name](*arguments)
            else:
                return f"Error: Function '{function_name}' not found."
        else:
            return "No function call found in the raw string."


if __name__ == "__main__":
    task_executor = ToolExecutor()
    raw_str = """Thought: I need to create a task for the homework due tomorrow.
Action: get_note("xz")"""

    print(task_executor.execute_from_string(raw_str))
