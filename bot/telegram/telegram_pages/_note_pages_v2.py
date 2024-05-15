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
from bot.telegram.ui_templates import show_notes_list
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

    
    async def client_get_page_content(self, chat_id, page_token):
        return await self.client.get_note_page_content(chat_id, page_token)
    
    async def client_get_total_pages(self, chat_id: int) -> int:
        return await self.client.get_total_note_pages(chat_id)        
    
    def check_match_pattern(self, query: CallbackQuery) -> bool:
        return query.data.startswith(f'{NOTE_PAGE_CHAR}{PAGE_DELIMITER}')

    async def _preview_page_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        print('preview page callback')
        if self.check_match_pattern(query):
            page_token = query.data.split(PAGE_DELIMITER)[1]
            await self.show_preview_page(query, context, page_token)

    async def show_preview_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, starting_point: str | None = None) -> None:
        chat_id = update.effective_chat.id

        starting_point = int(starting_point) if starting_point else 0

        resp_data = await self.client.get_note_page_content(chat_id, starting_point)
        titles = []
        notes_tokens = []

        for q in resp_data:
            props = q['properties']
            token = q['id']
            title = " ".join([string['plain_text'] for string in props['Name']['title']])

            notes_tokens.append(token)
            titles.append(title)

        if not titles:
            # edit message
            message = await update.message.reply_text(
                text='There is no note yet',
                reply_markup=None
            )
        
        else:
            template = show_notes_list(chat_id, titles, notes_tokens, starting_point)

            message = await update.message.reply_text(
                text=template['text'],
                reply_markup=template['reply_markup'],
                parse_mode=template['parse_mode']

                )


        context.user_data['review_pages_message_id'] = message.message_id
            






            



