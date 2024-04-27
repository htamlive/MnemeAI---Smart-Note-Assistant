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
import re

class NotePages:
    def __init__(self, application, client) -> None:
        self.application = application
        self.client = client
        self.init_view_note_page_command()
        self.init_note_pages()

    def init_view_note_page_command(self) -> None:
        async def view_note_page_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            paginator = self.init_pagination(1)
            await update.message.reply_text(
                text=self.client.get_note_content_at_page(0),
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )

        self.application.add_handler(CommandHandler('view_notes', view_note_page_command))

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

    
    def init_note_pages(self) -> None:
        async def note_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query: CallbackQuery = update.callback_query

            await query.answer()
            
            if re.match(r'p#(\d+)', query.data):
                page = int(query.data.split('#')[1])

                paginator = self.init_pagination(page)

                await query.edit_message_text(
                    text=self.client.get_note_content_at_page(page - 1),
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



        self.application.add_handler(CallbackQueryHandler(note_page_callback))