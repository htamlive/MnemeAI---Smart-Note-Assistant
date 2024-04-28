from telegram import (
    Update, 
    InlineKeyboardButton,
    CallbackQuery
    )
from telegram.ext import (
    CallbackQueryHandler, ContextTypes, CommandHandler
)
from telegram_bot_pagination import InlineKeyboardPaginator
from test import pagination_test_data
from client import Client
import re

class NotePages:
    def __init__(self, client: Client) -> None:
        self.client = client
        # self.init_view_note_page_command()
        # self.init_note_pages()

    async def view_note_page_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        paginator = self.init_pagination(1)
        message = await update.message.reply_text(
            text=self.client.get_note_content_at_page(1),
            reply_markup=paginator.markup,
            parse_mode='Markdown'
        )

        context.user_data['note_pages_message_id'] = message.message_id


    def init_pagination(self, page) -> InlineKeyboardPaginator:
        paginator = InlineKeyboardPaginator(
                len(pagination_test_data),
                current_page=page,
                data_pattern='p#{page}'
            )
        
        paginator.add_after(
            InlineKeyboardButton('Back', callback_data='back')                
            )
        
        return paginator

    
    async def note_page_callback(self, query) -> None:        
        if re.match(r'p#(\d+)', query.data):
            page = int(query.data.split('#')[1])

            paginator = self.init_pagination(page)

            await query.edit_message_text(
                text=self.client.get_note_content_at_page(page),
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )

            return
        elif(query.data == 'back'):
            await query.edit_message_text(
                text='Done reviewing!',
                parse_mode='Markdown'
            )
            return



