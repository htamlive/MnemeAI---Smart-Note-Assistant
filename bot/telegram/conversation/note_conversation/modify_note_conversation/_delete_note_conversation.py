from telegram import (
    Update, CallbackQuery
)
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)

from telegram import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
from ._modify_note_conversation import ModifyNoteConversation

from client import TelegramClient

from bot.telegram.ui_templates import get_note_option_keyboard, get_delete_note_confirmation_keyboard

from config import PATTERN_DELIMITER, Patterns

class DeleteNoteConversation(ModifyNoteConversation):
    def __init__(self, DELETE_NOTE: int, VIEW_NOTES, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.DELETE_NOTE = DELETE_NOTE
        self.VIEW_NOTES = VIEW_NOTES
        self._states = [CallbackQueryHandler(self.handle_confirmation)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()

        note_idx = query.data.split(PATTERN_DELIMITER)[1]
        keyboard = self.get_confirmation_keyboard(note_idx)

        current_text = query.message.text
        await query.edit_message_text(text=current_text, reply_markup=InlineKeyboardMarkup(keyboard))
        await query.message.reply_text("Are you really sure you want to delete?\n""Becareful, this action is irreversible.")

        return self.DELETE_NOTE


    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query: CallbackQuery = update.callback_query
        await query.answer()

        if query.data.startswith(Patterns.CONFIRM_DELETE_NOTE.value):
            chat_id = query.message.chat_id

            note_idx = query.data.split(PATTERN_DELIMITER)[1]
            await self.client_delete(chat_id, note_idx)
            await self.on_finish_edit(update, context)

            return ConversationHandler.END
        elif query.data.startswith(Patterns.CANCEL_DELETE_NOTE.value):
            note_idx = query.data.split(PATTERN_DELIMITER)[1]
            await self.restore_item_content(query, note_idx)

            return self.VIEW_NOTES

    async def client_delete(self, chat_id: int, idx: int) -> None:
        await self.client.delete_note(chat_id, idx)

    async def restore_item_content(self, query: CallbackQuery, note_idx: str) -> None:
        chat_id = query.message.chat_id
        note_content = await self.client_get_content(chat_id, note_idx)
        keyboard = self.get_option_keyboard(note_idx)
        print(note_content)
        await query.edit_message_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    def get_option_keyboard(self, idx: int) -> list[list[InlineKeyboardButton]]:
        return get_note_option_keyboard(idx)

    def get_confirmation_keyboard(self, idx: int) -> list[list[InlineKeyboardButton]]:
        return get_delete_note_confirmation_keyboard(idx)

    def client_get_content(self, chat_id: int, idx: int) -> str:
        return self.client.get_note_content(chat_id, idx)

