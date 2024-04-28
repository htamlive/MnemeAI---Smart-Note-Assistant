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
from client import Client


class ViewNotesConversation(CommandConversation):
    def __init__(self, VIEW_NOTES: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: Client, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.VIEW_NOTES = VIEW_NOTES
        self.EDIT_TITLE = EDIT_TITLE
        self.EDIT_DETAIL = EDIT_DETAIL

        self._states = [
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_view_a_note),
            CallbackQueryHandler(self.handle_option_callback)
            
            ]
        
        self.note_pages = NotePages(self.client)

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        
        await self.note_pages.view_note_page_command(update, context)

        await update.message.reply_text("Please send me the note index.")

        return self.VIEW_NOTES
    
    async def receive_view_a_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        received_text = update.message.text
        await self.handle_view_a_note(update, context, received_text)
        return self.VIEW_NOTES
        # return ConversationHandler.END
        
    def get_modifying_option_keyboard(self, note_idx: str) -> list:
        keyboard = [
            [
                InlineKeyboardButton('Edit Title', callback_data=f'edit_note_title@{note_idx}'),
                InlineKeyboardButton('Edit Detail', callback_data=f'edit_note_detail@{note_idx}'),
                InlineKeyboardButton('Delete', callback_data=f'delete_note@{note_idx}')
            ],
            [InlineKeyboardButton('Back', callback_data='back')]
        ]
        return keyboard

    async def response_modifying_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_content, note_idx) -> None:
        keyboard = self.get_modifying_option_keyboard(note_idx)

        if('prev_review_note_message_id' in context.user_data):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['prev_review_note_message_id']
                )


        message = await update.message.reply_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

        context.user_data['prev_review_note_message_id'] = message.message_id

    async def handle_view_a_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_idx: str = None) -> None:
        chat_id = update.message.chat_id
        try:
            note_content = self.client.get_note_content(chat_id, note_idx)
        except Exception as e:
            note_content = str(e)
            await update.message.reply_text(note_content)
            return
        
        await self.response_modifying_options(update, context, note_content, note_idx)

    async def handle_option_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        await self.note_pages.note_page_callback(query)

        if query.data == 'back':
            await query.edit_message_text('Done editing!')

        return None

        
        
