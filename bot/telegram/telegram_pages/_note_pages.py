from telegram import (
    Update, 
    InlineKeyboardButton,
    CallbackQuery
    )
from telegram.ext import (
    CallbackQueryHandler, ContextTypes, CommandHandler
)
from bot.telegram.ui_templates import create_preview_pages
from telegram_bot_pagination import InlineKeyboardPaginator
from client import TelegramClient
import re

class NotePages:
    def __init__(self, client: TelegramClient) -> None:
        self.client = client
        # self.init_view_note_page_command()
        # self.init_note_pages()

    async def view_note_page_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        paginator: InlineKeyboardPaginator = self.init_preview_pages()
        chat_id = update.effective_chat.id
        message = await update.message.reply_text(
            text=self.client_get_content(chat_id, 1),
            reply_markup=paginator.markup,
            parse_mode='HTML'
        )

        context.user_data['review_pages_message_id'] = message.message_id

    def client_get_content(self, chat_id, note_idx) -> str:
        return self.client.get_note_content(chat_id, note_idx)
    
    def client_get_total_pages(self) -> int:
        return self.client.get_total_note_pages()
    
    def init_preview_pages(self, page: int = 1) -> InlineKeyboardPaginator:
        return create_preview_pages(self.client_get_total_pages(), page)

    
    async def note_page_callback(self, query: CallbackQuery) -> None:       
        if re.match(r'p#(\d+)', query.data):
            page = int(query.data.split('#')[1])
            chat_id = query.message.chat_id

            paginator = self.init_preview_pages(page)

            try:
                text = self.client_get_content(chat_id, page)
                await query.edit_message_text(
                    text=text,
                    reply_markup=paginator.markup,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f'Error in note_page_callback: {e}')
                await query.edit_message_text(
                    text='There is some error, please view the latest version',
                    parse_mode='HTML'
                )

                # send new message
                paginator = self.init_preview_pages()
                await query.message.reply_text(
                    text=self.client_get_content(chat_id, 1),
                    reply_markup=paginator.markup,
                    parse_mode='HTML'
                )


            return
        elif(query.data == 'back'):
            await query.edit_message_text(
                text='Done reviewing!',
                parse_mode='HTML'
            )
            return



