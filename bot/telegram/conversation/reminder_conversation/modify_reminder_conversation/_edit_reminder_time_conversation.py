from ...note_conversation.modify_note_conversation import ModifyNoteConversation
from client import TelegramClient
from telegram import Update, CallbackQuery

from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from config import PATTERN_DELIMITER

class EditReminderTimeConversation(ModifyNoteConversation):
    def __init__(self, EDIT_TITLE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.EDIT_TITLE = EDIT_TITLE
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_time_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        reminder_idx = query.data.split(PATTERN_DELIMITER)[1]
        
        context.user_data['item_idx'] = reminder_idx
        await query.message.reply_text("Please send me the new time of your note.")
        
        return self.EDIT_TITLE
    
    async def receive_time_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        time_text = update.message.text
        await self.handle_receive_time(update, context, time_text)

        await self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def handle_receive_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['item_idx']

        response_text = await self.save_time(chat_id, note_idx, time_text)
        await update.message.reply_text(response_text)

    async def save_time(self, chat_id: int, idx: int, time: str) -> str:
        return await self.client_save_time(chat_id, idx, time)
    
    async def client_save_time(self, chat_id: int, idx: int, time_text: str) -> str:
        return await self.client.save_reminder_time(chat_id, idx, time_text)