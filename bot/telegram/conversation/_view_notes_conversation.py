from ._command_conversation import (
    CommandConversation, MessageHandler
)
from telegram import (
    Update, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler, filters, CallbackQueryHandler
)

import re

from ..telegram_pages import NotePages
from client import TelegramClient

from bot.telegram.ui_templates import get_note_option_keyboard

class ViewNotesConversation(CommandConversation):
    def __init__(self, VIEW_NOTES: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.VIEW_NOTES = VIEW_NOTES
        self.EDIT_TITLE = EDIT_TITLE
        self.EDIT_DETAIL = EDIT_DETAIL

        self._states = [
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_preview),
            ]
        
        self.previewing_pages = self.init_reviewing_pages()

    def add_preview_pages_callback(self, application) -> None:
        application.add_handler(CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern='^n#'))

    def share_preview_page_callback(self) -> CallbackQueryHandler:
        return CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern='^n#')

    def handle_preview_page_callback(self, callbacks: list) -> None:
        self._states += callbacks
        
    def init_reviewing_pages(self) -> NotePages:
        return NotePages(self.client)

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        
        await self.previewing_pages.view_note_page_command(update, context)

        await update.message.reply_text("Please send me the note index.")

        return self.VIEW_NOTES
    
    async def receive_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        received_text = update.message.text
        await self.handle_preview(update, context, received_text)
        return self.VIEW_NOTES
        # return ConversationHandler.END


    async def response_modifying_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_content, note_idx) -> None:
        keyboard = self.get_option_keyboard(note_idx)

        if('prev_review_message' in context.user_data):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['prev_review_message'][0]
                )


        message = await update.message.reply_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        context.user_data['prev_review_message'] = (message.message_id, message.text_html)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_note_option_keyboard(note_idx)

    async def handle_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_idx: str = None) -> None:
        chat_id = update.message.chat_id
        try:
            note_content = self.client_get_content(chat_id, int(note_idx))
        except Exception as e:
            note_content = str(e)
            await update.message.reply_text(note_content)
            return
        
        await self.response_modifying_options(update, context, note_content, note_idx)


    
    def client_get_content(self, chat_id: int, idx: int) -> str:
        return self.client.get_note_content(chat_id, idx)

        
        
