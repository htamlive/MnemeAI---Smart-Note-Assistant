
from typing import List
from ._note_pages_v3 import NotePages

from client import TelegramClient

from bot.telegram.ui_templates import get_reminder_option_keyboard, show_reminders_list_v2 as show_reminders_list, render_html_reminder_detail

from telegram import CallbackQuery

from config import REMINDER_PAGE_CHAR, PAGE_DELIMITER

from pkg.google_task_api.model import ListTask, Task

from config import REMINDER_PAGE_CHAR

from telegram.ext import  ContextTypes

class ReminderPages(NotePages):
    def __init__(self, client: TelegramClient) -> None:
        super().__init__(client)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx) 

    
    def check_match_pattern(self, query: CallbackQuery) -> bool:

        return query.data.startswith(f'{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}')
    
    async def client_get_total_pages(self, chat_id: int) -> int:
        return await self.client.get_total_reminder_pages(chat_id)
    
    async def client_get_page_content(self, chat_id, page_token):
        return await self.client.get_reminder_page_content(chat_id, page_token)

    async def show_preview_page(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, cur_page_token: str | None = None) -> None:
        chat_id = query.message.chat_id
        page_content: ListTask | None = await self.client_get_page_content(chat_id, cur_page_token)

        items: List[Task] = page_content.items

        if not items:
            await query.message.reply_text(
                text='There is no reminder yet',
                reply_markup=None
            )
        
        else:

            titles = [item.title for item in items]
            tokens = [item.id for item in items]
            next_page_token = page_content.nextPageToken

            result = show_reminders_list(chat_id=chat_id, titles=titles, reminder_tokens=tokens, next_page_token=next_page_token, cur_page_token=cur_page_token)


            message = await query.message.reply_text(
                text=result['text'],
                reply_markup=result['reply_markup'],
                parse_mode='HTML'
            )

            context.user_data['review_pages_message_id'] = message.message_id
    