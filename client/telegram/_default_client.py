from datetime import datetime, timezone
from typing import Tuple

from django.utils import timezone as dj_timezone

import os

import dotenv
import pytz

# import datetime
from pkg.google_task_api.model import ListTask
from pkg.model import ReminderCeleryTask
from telegram.ext import CallbackContext
from telegram import Update
from pkg.msg_brokers.celery import send_notification
from test import pagination_test_data
from config import *
from urllib.parse import quote
from pkg.google_task_api.client import GoogleTaskClient as GoogleTaskClient, Task
from pkg.google_task_api.authorization_client import Authorization_client

from asgiref.sync import sync_to_async
import datetime
import time


# from pkg.reminder.task_queues import queue_task

from llm.llm import LLM
from llm._tools import save_task_title, save_task_detail, delete_task
from llm.models import UserData

import warnings
import functools

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


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
        return await self.llm.execute_prompting(UserData(chat_id=chat_id), prompt)

    async def save_remind(self, chat_id, remind_text) -> str:
        prompt = f"Add reminder: {remind_text}"
        return await self.llm.add_task(UserData(chat_id=chat_id), prompt)

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

    @deprecated
    def get_total_note_pages(self, chat_id: int) -> int:
        return len(pagination_test_data)

    # ================= Reminder/Task =================
    @deprecated
    def _extract_reminder_idx(self, reminder_idx_text) -> int:
        """
        May use LLM to extract reminder index from text
        """

        # this is 1-based index -> 0-based index
        return int(reminder_idx_text) - 1

    async def get_reminder_content(self, chat_id, reminder_token) -> Tuple[str, str, str]:  # [title, description, due
        client = self.google_task_client
        task = await sync_to_async(client.get_task)(chat_id=chat_id, task_id=reminder_token)

        reminder = await sync_to_async(ReminderCeleryTask.objects.get)(chat_id=chat_id, reminder_id=reminder_token)

        # get time zone dynamically
        due = dj_timezone.localtime(reminder.due).strftime("Due time: %H:%M %A %d %B %Y")

        title, description = task.title, task.notes

        return title, description, due
        # return f'{title} ' + '<a href="href="tg://bot_command?command=start" onclick="execBotCommand(this)">edit</a>' + '{time}{description}'

    @deprecated
    async def get_reminder_content_at_page(self, chat_id, page_token) -> str:
        return await self.get_reminder_content(chat_id, page_token)

    async def delete_reminder(self, chat_id, token) -> str:
        return await delete_task(UserData(chat_id=chat_id, reminder_token=token), google_task_client=self.google_task_client)
    
    async def save_reminder_title(self, chat_id: int, reminder_token: str, title_text: str) -> str:
        return await save_task_title(UserData(chat_id=chat_id, reminder_token=reminder_token), title_text, google_task_client=self.google_task_client)
    
    async def save_reminder_detail(self, chat_id: int, reminder_token: str, detail_text: str) -> str:
        return await save_task_detail(UserData(chat_id=chat_id, reminder_token=reminder_token), detail_text, google_task_client=self.google_task_client)

    async def save_reminder_time(self, chat_id: int, reminder_token: str, time_text: str) -> str:
        prompt = f"Set reminder time: {time_text}"
        return await self.llm.save_task_time(UserData(chat_id=chat_id, reminder_token=reminder_token), prompt)

    async def get_note_page_content(self, chat_id, page_token) -> ListTask | None:
        return await sync_to_async(self.google_task_client.list_tasks)(chat_id=chat_id, page_token=page_token) 

    @deprecated
    async def remove_task(self, chat_id: int, token: str) -> None:
        client = self.google_task_client
        await sync_to_async(client.delete_task)(
            chat_id=chat_id,
            task_id=token,
        )
        # Cancel the Celery task
        reminder = await sync_to_async(ReminderCeleryTask.objects.filter)(
            chat_id=chat_id,
            reminder_id=token,
            completed=False,
        )
        await sync_to_async(reminder.update)(state=ReminderCeleryTask.REVOKED)

    @deprecated
    async def get_total_reminder_pages(self, chat_id: int) -> int:
        tasks = await sync_to_async(self.google_task_client.list_tasks)(chat_id=chat_id)
        if tasks is None:
            return 0
        return len(tasks.items)
    

    # ================= Other =================

    async def process_prompt(self, user_data: UserData, prompt_text: str) -> Tuple[str, str]:
        # response = requests.post(
        #     f"{self.SERVER_URL}/prompt",
        #     json={"chat_id": chat_id, "prompt_text": prompt_text},
        # ).json()

        # print(response)

        return await self.llm.execute_prompting(user_data, prompt_text), END

        # return response["result"]["response_text"], response["result"]["next_state"]

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
