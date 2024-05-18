from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from bot.telegram.utils import check_data_requirement
from ._modify_note_conversation import ModifyNoteConversation
from client import TelegramClient
from config import PATTERN_DELIMITER

class EditNoteDetailConversation(ModifyNoteConversation):
    def __init__(self, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.EDIT_DETAIL = EDIT_DETAIL
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_detail_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        success, message = self.check_data_requirement(context)

        if not success:
            await update.message.reply_text(message)
            return ConversationHandler.END
        
        query = update.callback_query
        await query.answer()

        note_token = self.extract_hidden_token(query)
        context.user_data['item_idx'] = note_token

        await query.message.reply_text("Please send me the new detail of your note.")
        return self.EDIT_DETAIL
    
    async def receive_detail_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        detail_text = update.message.text
        await self.handle_receive_detail_text(update, context, detail_text)
        await self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def handle_receive_detail_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, detail_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['item_idx']
        response_text = await self.client_save_detail(chat_id, note_idx, detail_text)
        await update.message.reply_text(response_text)

    async def client_save_detail(self, chat_id: int, idx: int, detail_text: str) -> str:
        response_text = await self.client.save_note_detail(chat_id, idx, detail_text)
        return response_text
