from datetime import datetime, timezone
import os

import dotenv

# import datetime
from pkg.model.reminder_cele_task import ReminderCeleryTask
from pkg.msg_brokers.tasks import send_notification
from telegram.ext import CallbackContext
from telegram import Update
from test import pagination_test_data
import requests
from config import *
from urllib.parse import quote
from pkg.google_task_api.client import Client as GoogleTaskClient, Task
from pkg.google_task_api.authorization_client import Authorization_client

from asgiref.sync import sync_to_async
import datetime
# from pkg.reminder.task_queues import queue_task


class DefaultClient:
    def __init__(self) -> None:
        import dotenv
        import os

        dotenv.load_dotenv()
        self.TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
        self.SERVER_URL = os.getenv("SERVER_URL")

        redirected_url = quote(f"{self.SERVER_URL}/login/notion/authorized")
        self.NOTION_AUTH_URL = (
            f'{os.getenv("NOTION_AUTH_PREF")}&redirect_uri={redirected_url}'
        )

        self.API_BASE_URL = f"https://api.telegram.org/bot{self.TELEBOT_TOKEN}/"
        # https://core.telegram.org/bots/api
        self.google_task_client = GoogleTaskClient()
        self.authorization_client = Authorization_client()

    async def user_subscribe(self, chat_id):
        pass

    async def save_note(self, chat_id, note_text) -> str:
        return f"Note saved: {note_text}"

    async def save_remind(self, chat_id, remind_text) -> str:
        '''
            LLM in action
        '''

        title = "Title"
        duedate = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return self.save_reminder(chat_id, title, remind_text, duedate)

    # ================= Note =================

    async def save_note_title(self, chat_id, note_idx, title_text):
        return f"Title saved: {title_text}"

    async def save_note_detail(self, chat_id, note_idx, detail_text):
        return f"Detail saved: {detail_text}"

    async def delete_note(self, chat_id, page) -> str:
        return f"Note deleted at page {page}"

    def get_note_content_at_page(self, chat_id, page) -> str:
        return self.get_note_content(chat_id, page)

    def extract_note_idx(self, note_idx_text) -> int:
        """
        May use LLM to extract note index from text
        """

        # this is 1-based index -> 0-based index
        return int(note_idx_text) - 1

    def get_note_content(self, chat_id, note_idx_text) -> str:

        # Remember to convert to 0-based index
        note_idx = self.extract_note_idx(note_idx_text)

        title = pagination_test_data[note_idx]["title"]
        description = pagination_test_data[note_idx]["description"]

        return f"<b>YOUR NOTES</b>\n\n\n<b><i>{title}</i></b>\n\n{description}"

    def get_total_note_pages(self, chat_id: int) -> int:
        return len(pagination_test_data)

    # ================= Reminder/Task =================

    def _extract_reminder_idx(self, reminder_idx_text) -> int:
        """
        May use LLM to extract reminder index from text
        """

        # this is 1-based index -> 0-based index
        return int(reminder_idx_text) - 1

    async def get_reminder_content(self, chat_id, idx) -> str:
        reminder_indx = self._extract_reminder_idx(idx)
        client = self.google_task_client
        tasks = await sync_to_async(client.list_tasks)(chat_id=chat_id)
        if tasks is None:
            return "No reminder found"
        if len(tasks.items) <= reminder_indx:
            return "Reminder not found"
        title, description, time = (
            tasks.items[reminder_indx].title,
            tasks.items[reminder_indx].notes,
            tasks.items[reminder_indx].due,
        )
        # title = pagination_test_data[reminder_indx]["title"]
        # description = pagination_test_data[reminder_indx]["description"]
        # time = pagination_test_data[reminder_indx]["time"]
        html_render = f"<b>YOUR REMINDERS:</b>\n\n\n<b><i>{title}</i></b>\n{time}\n\n{description}"
        return html_render
        # return f'{title} ' + '<a href="href="tg://bot_command?command=start" onclick="execBotCommand(this)">edit</a>' + '{time}{description}'

    async def get_reminder_content_at_page(self, chat_id, page) -> str:
        return await self.get_reminder_content(chat_id, page)

    async def delete_reminder(self, chat_id, page) -> str:
        self.remove_task(chat_id, page)
        return self.delete_note(chat_id, page)

    # def _get_or_create_reminder(self, chat_id, idx) -> Reminder:
    #     reminder, has_created = Reminder.objects.get_or_create(chat_id=chat_id, id=idx)
    #     if has_created:
    #         reminder.updated_at = timezone.now()
    #     reminder.save()

    #     return reminder

    # async def save_reminder_title(self, chat_id: str, idx: int, title_text: str) -> str:
    #     reminder = self._get_or_create_reminder(chat_id, idx)

    #     client = GoogleTaskClient()
    #     task: Task | None = client.get_task(chat_id, reminder.task_id)
    #     if task is None:
    #         task = Task(chat_id=chat_id, id=id, title=title_text)
    #     else:
    #         task.title = title_text
    #     client.insert_task(chat_id, task)

    #     return f"Title saved: {title_text}"

    # async def save_reminder_detail(
    #     self, chat_id: str, idx: int, detail_text: str
    # ) -> str:
    #     reminder = self._get_or_create_reminder(chat_id, idx)

    #     client = GoogleTaskClient()
    #     task: Task | None = client.get_task(chat_id, reminder.task_id)
    #     if task is None:
    #         task = Task(chat_id=chat_id, id=id, notes=detail_text)
    #     else:
    #         task.notes = detail_text
    #     client.insert_task(chat_id, task)

    #     return f"Detail saved: {detail_text}"

    # async def save_reminder_time(self, chat_id: str, idx: int, time) -> str:
    #     reminder = self._get_or_create_reminder(chat_id, idx)

    #     client = GoogleTaskClient()
    #     task: Task | None = client.get_task(chat_id, reminder.task_id)
    #     if task is None:
    #         task = Task(chat_id=chat_id, id=id, due=time)
    #     else:
    #         task.due = time

    #     # Schedule a task to celery here
    #     # reminded_time is before 10 minutes
    #     # reminded_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.timedelta(minutes=10)
    #     # queue_task.apply_async(args=(chat_id, idx), eta=reminded_time)

    #     return f"Time edited: {time}"

    async def save_reminder(
        self, chat_id: int, title: str, details: str, due: datetime
    ) -> str:
        try:
            # Save the reminder by calling the Google Task API

            task = Task(title=title, notes=details, due=due.isoformat())
            result = self.google_task_client.insert_task(chat_id, task)
            if result is None:
                return "Task cannot be created"
            # Inserting the Celery task
            new_cele_task = ReminderCeleryTask(
                title=title,
                description=details,
                chat_id=chat_id,
                id=result.id,
                state=ReminderCeleryTask.PENDING,
            )
            new_cele_task.save()

            url = f"{self.API_BASE_URL}sendMessage"
            # Setting up the Celery task
            send_notification.apply_async(
                args=(url, chat_id, task.id),
                eta=due - datetime.timedelta(minutes=5),
                expires=due + datetime.timedelta(minutes=5),
            )
        except Exception as e:
            print(e)
            return "Task has been created but cannot be scheduled"
        return f"Reminder saved: {title}"

    def remove_task(self, chat_id: int, idx: str) -> None:
        try:
            client = self.google_task_client
            client.delete_task(
                chat_id=chat_id,
                task_id=idx,
            )
            # Cancel the Celery task
            cele_task = ReminderCeleryTask.objects.get(chat_id=chat_id, id=idx)
            cele_task.revoke()
            cele_task.save()
        except Exception as e:
            print(e)

    async def get_total_reminder_pages(self, chat_id: int) -> int:
        tasks = await sync_to_async(self.google_task_client.list_tasks)(chat_id=chat_id)
        if tasks is None:
            return 0
        return len(tasks.items)

    # ================= Other =================

    async def process_prompt(self, chat_id, prompt_text) -> str:
        response = requests.post(
            f"{self.SERVER_URL}/prompt",
            json={"chat_id": chat_id, "prompt_text": prompt_text},
        ).json()

        print(response)

        return response["result"]["response_text"], response["result"]["next_state"]

        # ở state Note_text nhưng muốn view note
        # /ah cho tôi xem note -> gửi một message mà chứa bảng note, VIEW_NOTE

    def get_jobs_from_start(self, update: Update) -> list:
        async def notify_assignees(context: CallbackContext) -> None:
            # await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello')
            print("sent message")

        # (function, interval in seconds)
        return [
            # (notify_assignees, 5)
        ]

    def get_notion_authorization_url(self, chat_id: int) -> str:
        return self.NOTION_AUTH_URL

    async def get_google_authorization_url(self, chat_id: int) -> str:
        url = await sync_to_async(self.authorization_client.get_auth_url)(chat_id)
        return url

    def check_notion_authorization(self, chat_id: int) -> bool:
        return False

    async def check_google_authorization(self, chat_id: int) -> bool:

        credential = await sync_to_async(self.authorization_client.get_credentials)(
            chat_id
        )
        return credential is not None
