from bot.telegram.utils import check_data_requirement
from llm.models import UserData
from ...note_conversation.modify_note_conversation import ModifyNoteConversation
from client import TelegramClient
from telegram import Update, CallbackQuery


from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackContext
)

from config import PATTERN_DELIMITER

class EditReminderTimeConversation(ModifyNoteConversation):
    def __init__(self, EDIT_TITLE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.EDIT_TITLE = EDIT_TITLE
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_time_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        success, message = self.check_data_requirement(context)

        if not success:
            await update.message.reply_text(message)
            return ConversationHandler.END

        query: CallbackQuery = update.callback_query
        await query.answer()
        reminder_idx = super().extract_hidden_token(query)
        
        context.user_data['item_idx'] = reminder_idx
        await query.message.reply_text("Please send me the new time of your note.")
        
        return self.EDIT_TITLE
    
    def check_data_requirement(self, context: CallbackContext.DEFAULT_TYPE) -> tuple:
        return check_data_requirement(context)
    
    async def receive_time_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        time_text = update.message.text
        await self._handle_receive_time(update, context, time_text)

        await self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def _handle_receive_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['item_idx']

        timezone = context.user_data.get('timezone', None)

        response_text = await self.client_save_time(chat_id, note_idx, time_text, timezone)
        await update.message.reply_text(response_text)


    
    async def client_save_time(self, chat_id: int, token: int, time_text: str, timezone: str) -> str:
        return await self.client.save_reminder_time(
            user_data=UserData(chat_id=chat_id, timezone=timezone, reminder_token=token),
            time_text=time_text
        )