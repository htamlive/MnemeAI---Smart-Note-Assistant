
from typing import List
from ._note_pages_v2 import NotePages

from client import TelegramClient

from bot.telegram.ui_templates import get_reminder_option_keyboard, create_preview_pages

from telegram_bot_pagination import InlineKeyboardPaginator

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import REMINDER_PAGE_CHAR, PAGE_DELIMITER, DETAIL_REMINDER_CHAR

from pkg.google_task_api.model import ListTask, Task

from config import REMINDER_PAGE_CHAR

import re

from telegram.ext import  ContextTypes

class ReminderPages(NotePages):
    def __init__(self, client: TelegramClient) -> None:
        super().__init__(client)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx) 

    
    def check_match_pattern(self, query: CallbackQuery) -> bool:

        return re.match(REMINDER_PAGE_CHAR + r'#(\d+)', query.data)
    
    def client_get_content(self, chat_id, note_idx) -> str:
        return self.client.get_reminder_content(chat_id, note_idx)
    
    async def client_get_total_pages(self, chat_id: int) -> int:
        return await self.client.get_total_reminder_pages(chat_id)

    async def show_preview_page(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, cur_page_token: str | None = None) -> None:
        chat_id = query.message.chat_id
        page_content: ListTask | None = await self._client_get_page_content(chat_id, cur_page_token)

        items: List[Task] = page_content.items

        if not items:
            # edit message
            await query.message.reply_text(
                text='There is no reminder yet',
                reply_markup=None
            )
        
        else:
            keyboards = []

            count_items = len(items)
            for item in items:
                keyboards.append([InlineKeyboardButton(item.title, callback_data=f'{DETAIL_REMINDER_CHAR}{PAGE_DELIMITER}{item.id}')])
            
            next_page_token = page_content.nextPageToken
            if next_page_token:
                keyboards.append([InlineKeyboardButton('Show more', callback_data=f'{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}{next_page_token}')])

            text = 'Here are your reminders:\n'
            if(count_items > 1):
                text = 'Here are your reminders:\n'
            elif(count_items == 1):
                text = 'Here is your reminder:\n'
            elif(count_items == 0):
                text = 'There is no reminder yet'

            message = await query.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboards)
                )


            context.user_data['review_pages_message_id'] = message.message_id
    