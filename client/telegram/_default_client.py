from datetime import datetime, timezone
import os

import dotenv

# import datetime
from pkg.google_task_api.model import ListTask
from pkg.model import ReminderCeleryTask
from telegram.ext import CallbackContext
from telegram import Update
from pkg.msg_brokers.celery import send_notification
from test import pagination_test_data
import requests
from config import *
from urllib.parse import quote
from pkg.google_task_api.client import GoogleTaskClient as GoogleTaskClient, Task
from pkg.google_task_api.authorization_client import Authorization_client

from asgiref.sync import sync_to_async
import datetime

# from pkg.reminder.task_queues import queue_task

from llm.llm import LLM


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
        self.llm = LLM()

    async def user_subscribe(self, chat_id):
        pass

    async def save_note(self, chat_id, note_text) -> str:
        prompt = f"Add note: {note_text}"
        return self.llm.execute_llm(chat_id, prompt)

    async def save_remind(self, chat_id, remind_text) -> str:
        """
        LLM in action
        """

        prompt = f"Add reminder: {remind_text}"
        return self.llm.execute_llm(chat_id, prompt)

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

    def get_note_content(self, chat_id, note_token) -> str:

        # Remember to convert to 0-based index
        note_idx = self.extract_note_idx(note_token)

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

    async def get_reminder_content(self, chat_id, reminder_token) -> str:
        client = self.google_task_client
        task = await sync_to_async(client.get_task)(chat_id=chat_id, task_id=reminder_token)

        title, description, time = task.title, task.notes, task.due


        # reminder_indx = self._extract_reminder_idx(reminder_token)
        # tasks = await sync_to_async(client.list_tasks)(chat_id=chat_id)
        # if tasks is None or len(tasks.items) <= reminder_indx:
        #     return "No reminder found in your Google Task list."
        # title, description, time = (
        #     tasks.items[reminder_indx].title,
        #     tasks.items[reminder_indx].notes,
        #     tasks.items[reminder_indx].due,
        # )
        # title = pagination_test_data[reminder_indx]["title"]
        # description = pagination_test_data[reminder_indx]["description"]
        # time = pagination_test_data[reminder_indx]["time"]
        html_render = f"<b>YOUR REMINDERS:</b>\n\n\n<b><i>{title}</i></b>\n{time}\n\n{description}"
        return html_render
        # return f'{title} ' + '<a href="href="tg://bot_command?command=start" onclick="execBotCommand(this)">edit</a>' + '{time}{description}'

    async def get_reminder_content_at_page(self, chat_id, page) -> str:
        return await self.get_reminder_content(chat_id, page)

    async def delete_reminder(self, chat_id, page) -> str:
        return await self.remove_task(chat_id, page)
        return self.delete_note(chat_id, page)

    async def save_reminder(
        self, chat_id: int, title: str, details: str, due: datetime
    ) -> str:
        # Save the reminder by calling the Google Task API\
        task = Task(
            title=title,
            notes=details,
            due=due.replace(tzinfo=timezone.utc).isoformat(),
        )
        result = await sync_to_async(self.google_task_client.insert_task)(chat_id, task)
        if result is None:
            return "Task cannot be created"
        # Inserting the Celery task
        await sync_to_async(ReminderCeleryTask.objects.create)(
            title=title,
            description=details,
            chat_id=chat_id,
            reminder_id=result.id,
            state=ReminderCeleryTask.PENDING,
        )
        # Setting up the Celery task
        await sync_to_async(send_notification.apply_async)(
            args=(chat_id, result.id),
            countdown = (due - datetime.datetime.now()).total_seconds(),
            expires=due + datetime.timedelta(minutes=5),
        )
        return f"Reminder saved: {title}"

    async def remove_task(self, chat_id: int, idx: str) -> None:
        client = self.google_task_client
        tasks = await sync_to_async(client.list_tasks)(chat_id=chat_id)
        to_be_removed_task = None
        if tasks.items is not None:
            to_be_removed_task = tasks.items[int(idx) - 1]
        if to_be_removed_task is None:
            return
        await sync_to_async(client.delete_task)(
            chat_id=chat_id,
            task_id=to_be_removed_task.id,
        )
        # Cancel the Celery task
        reminder = await sync_to_async(ReminderCeleryTask.objects.filter)(
            chat_id=chat_id,
            reminder_id=to_be_removed_task.id,
            completed=False,
        )
        await sync_to_async(reminder.update)(state=ReminderCeleryTask.REVOKED)

    async def get_total_reminder_pages(self, chat_id: int) -> int:
        tasks = await sync_to_async(self.google_task_client.list_tasks)(chat_id=chat_id)
        if tasks is None:
            return 0
        return len(tasks.items)
    
    async def get_note_page_content(self, chat_id, page_token) -> ListTask | None:
        return await sync_to_async(self.google_task_client.list_tasks)(chat_id=chat_id, page_token=page_token) 

    # ================= Other =================

    async def process_prompt(self, chat_id, prompt_text) -> str:
        # response = requests.post(
        #     f"{self.SERVER_URL}/prompt",
        #     json={"chat_id": chat_id, "prompt_text": prompt_text},
        # ).json()

        # print(response)

        return self.llm.execute_llm(chat_id, prompt_text), END

        # return response["result"]["response_text"], response["result"]["next_state"]

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
