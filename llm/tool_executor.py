import datetime
import re
import ast
from typing import List

from pkg.google_calendar_api.client import GoogleCalendarApi
from pkg.google_calendar_api.model import CalendarEvent
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.celery import send_notification


# Define mock functions
def create_task(chat_id: int, title: str, body: str, due) -> str:
    # Save the reminder by calling the Google Task API
    event = CalendarEvent(
        summary=title,
        description=body,
        start=CalendarEvent.DateTime(
            date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
        end=CalendarEvent.DateTime(
            date=due,
        ),
    )
    google_calendar_client = GoogleCalendarApi()
    result = google_calendar_client.insert_event(chat_id, event)
    if result is None:
        return "Event cannot be created"
    # Inserting the Celery task
    ReminderCeleryTask.objects.create(
        title=title,
        description=body,
        chat_id=chat_id,
        reminder_id=result.id,
        state=ReminderCeleryTask.PENDING,
    )
    # Setting up the Celery task
    mapped_datetime = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
    send_notification.apply_async(
        args=(chat_id, result.id),
        countdown=(mapped_datetime - datetime.datetime.now()).total_seconds(),
        expires=mapped_datetime + datetime.timedelta(minutes=5),
    )
    return f"Created task: {title}, Body: {body}, Due: {due}"


def delete_task(chat_id: int, task_name: str) -> str:
    client = GoogleCalendarApi()
    events = client.list_events(chat_id=chat_id)
    to_be_removed_task = None
    if events.items is not None:
        to_be_removed_task = filter(
            lambda task: task.summary == task_name, events.items
        )
    if len(to_be_removed_task) == 0:
        return
    to_be_removed_task = to_be_removed_task[0]
    client.delete_event(
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

def add_note(chat_id: int, title: str, content: str) -> str:
    return f"Added note: {title}, Note: {content}"


def get_note(chat_id: int, queries_str: str) -> List[str]:
    return ["Building a rocket", "fighting a mummy", "climbing up the Eiffel Tower"]


# @traceable
class ToolExecutor:

    async def execute_from_string(
        self, user_data, raw_str, function_map: dict[str, callable]
    ) -> str:
        # Extract function call string using regular expression
        function_call_match = re.search(r"(\w+)\((.*?)\)", raw_str)

        if function_call_match:
            # Extract function name and its arguments
            function_name = function_call_match.group(1)

            arguments_str = function_call_match.group(2)

            if arguments_str == "":
                arguments_str = "()"

            # Parse arguments string into a Python literal
            try:

                arguments = ast.literal_eval(arguments_str)

                # If the argument is a single value, convert it to a tuple
                if not isinstance(arguments, tuple):
                    arguments = (arguments,)

                arguments = (user_data, *arguments)
            except (SyntaxError, ValueError):
                return "Error: Failed to parse arguments string."

            # Check if function exists
            if function_name in function_map:
                # Execute the function call
                return await function_map[function_name](*arguments)
            else:
                return f"Error: Function '{function_name}' not found."
        else:
            return "No function call found in the raw string."


if __name__ == "__main__":
    task_executor = ToolExecutor()
    raw_str = """Thought: I need to create a task for the homework due tomorrow.
Action: get_note("xz")"""

    print(task_executor.execute_from_string(raw_str))
