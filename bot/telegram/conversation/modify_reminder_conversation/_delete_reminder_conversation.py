

from client import Client
from ..modify_note_conversation._delete_note_conversation import DeleteNoteConversation
from client import Client
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.telegram.ui_templates import get_reminder_option_keyboard, get_delete_reminder_confirmation_keyboard

class DeleteReminderConversation(DeleteNoteConversation):
    def __init__(self, DELETE_REMINDER: int, VIEW_REMINDERS, client: Client, debug: bool = True) -> None:
        super().__init__(DELETE_REMINDER, VIEW_REMINDERS, client, debug)

    async def client_delete(self, chat_id: int, idx: int) -> None:
        await self.client.delete_reminder(chat_id, idx)

    async def client_get_content(self, chat_id: int, idx: int) -> str:
        return await self.client.get_reminder_content(chat_id, idx)
    
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()

        reminder_idx = query.data.split('@')[1]
        keyboard = self.get_confirmation_keyboard(reminder_idx)
        await query.edit_message_text(text="Are you really sure you want to delete?", reply_markup=InlineKeyboardMarkup(keyboard))

        return self.DELETE_NOTE
    
    def get_option_keyboard(self, note_idx: int) -> list:
        return get_reminder_option_keyboard(note_idx)
    
    def get_confirmation_keyboard(self, note_idx: int) -> list:
        return get_delete_reminder_confirmation_keyboard(note_idx)