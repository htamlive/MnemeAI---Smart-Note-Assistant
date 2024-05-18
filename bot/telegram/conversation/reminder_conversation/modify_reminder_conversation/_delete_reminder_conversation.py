

from bot.telegram.utils import check_data_requirement
from client import TelegramClient
from llm.models import UserData
from ...note_conversation.modify_note_conversation._delete_note_conversation import DeleteNoteConversation
from client import TelegramClient
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Patterns, PATTERN_DELIMITER
from telegram.ext import ConversationHandler
from telegram.ext import CallbackContext

from bot.telegram.ui_templates import get_reminder_option_keyboard, get_delete_reminder_confirmation_keyboard

class DeleteReminderConversation(DeleteNoteConversation):
    def __init__(self, DELETE_REMINDER: int, VIEW_REMINDERS, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(DELETE_REMINDER, VIEW_REMINDERS, client, debug)

    async def client_delete(self, chat_id: int, idx: int) -> None:
        await self.client.delete_reminder(chat_id, idx)

    async def client_get_content(self, chat_id: int, idx: int) -> str:
        return await self.client.get_reminder_content(UserData(chat_id=chat_id, reminder_token=idx))

    def check_data_requirement(self, context) -> tuple:
        return check_data_requirement(context)

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        success, message_text = check_data_requirement(context)

        query: CallbackQuery = update.callback_query
        if not success:
            await query.message.reply_text(message_text)
            return ConversationHandler.END

        await query.answer()

        reminder_idx = super().extract_hidden_token(query)
        keyboard = self.get_confirmation_keyboard(reminder_idx)
        await query.edit_message_text(text="Are you really sure you want to delete?", reply_markup=InlineKeyboardMarkup(keyboard))

        return self.DELETE_ITEM

    def get_option_keyboard(self, note_idx: int) -> list:
        return get_reminder_option_keyboard(note_idx)

    def get_confirmation_keyboard(self, note_idx: int) -> list:
        return get_delete_reminder_confirmation_keyboard(note_idx)

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query: CallbackQuery = update.callback_query
        await query.answer()

        if query.data.startswith(Patterns.CONFIRM_DELETE_REMINDER.value):
            chat_id = query.message.chat_id

            reminder_idx = query.data.split(PATTERN_DELIMITER)[1]
            await self.client_delete(chat_id, reminder_idx)
            await self.on_finish_edit(update, context)

            return ConversationHandler.END
        elif query.data.startswith(Patterns.CANCEL_DELETE_REMINDER.value):
            reminder_idx = query.data.split(PATTERN_DELIMITER)[1]
            await self.restore_item_content(query, reminder_idx)

            return self.VIEW_ITEMS