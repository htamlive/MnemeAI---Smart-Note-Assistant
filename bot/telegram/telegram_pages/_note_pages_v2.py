from typing import List
from telegram import (
    InlineKeyboardMarkup,
    Update,
    InlineKeyboardButton,
    CallbackQuery
    )
from telegram.ext import (
    CallbackQueryHandler, ContextTypes
)
from client import TelegramClient
import re
from config import NOTE_PAGE_CHAR, PAGE_DELIMITER, DETAIL_NOTE_CHAR
from pkg.google_task_api.model import ListTask, Task

class NotePages:
    def __init__(self, client: TelegramClient) -> None:
        self.client = client
        # self.init_view_note_page_command()
        # self.init_note_pages()

    async def view_note_page_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        

        await self.show_preview_page(update, context)

    
    def _client_get_page_content(self, chat_id, page_token):
        return self.client.get_note_page_content(chat_id, page_token)

    def client_get_content(self, chat_id, note_idx) -> str:
        return self.client.get_note_content(chat_id, note_idx)
    
    async def client_get_total_pages(self, chat_id: int) -> int:
        return await self.client.get_total_note_pages(chat_id)        
    
    def check_match_pattern(self, query: CallbackQuery) -> bool:
        return query.data.startswith(f'{NOTE_PAGE_CHAR}{PAGE_DELIMITER}')

    async def _preview_page_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        if self.check_match_pattern(query):
            page_token = query.data.split(PAGE_DELIMITER)[1]
            await self.show_preview_page(query, context, page_token)

    async def show_preview_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, cur_page_token: str | None = None) -> None:
        chat_id = update.effective_chat.id
        page_content: ListTask | None = await self._client_get_page_content(chat_id, cur_page_token)

        items: List[Task] = page_content['items']

        if not items:
            # edit message
            message = await update.message.reply_text(
                text='There is no note yet',
                reply_markup=None
            )
        
        else:
            keyboards = []

            count_items = len(items)
            for item in items:
                keyboards.append([InlineKeyboardButton(item['title'], callback_data=f'{DETAIL_NOTE_CHAR}{PAGE_DELIMITER}{item["id"]}')])
            
            next_page_token = page_content.get('nextPageToken')
            if next_page_token:
                keyboards.append([InlineKeyboardButton('Show more', callback_data=f'{NOTE_PAGE_CHAR}{PAGE_DELIMITER}{next_page_token}')])

            text = 'Here are your notes:\n'
            if(count_items > 1):
                text = 'Here are your notes:\n'
            elif(count_items == 1):
                text = 'Here is your note:\n'
            elif(count_items == 0):
                text = 'There is no note yet'

            message = await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboards)
                )


        context.user_data['review_pages_message_id'] = message.message_id
            






            



