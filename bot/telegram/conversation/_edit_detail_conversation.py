from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._edit_note_conversation import EditNoteConversation
from client import Client

class EditDetailConversation(EditNoteConversation):
    def __init__(self, EDIT_DETAIL: int, client: Client) -> None:
        self.client = client
        self.EDIT_DETAIL = EDIT_DETAIL
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_detail_text)]
        
    async def start_conservation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        note_idx = query.data.split('@')[1]
        context.user_data['note_idx'] = note_idx

        await update.message.reply_text("Please send me the new detail of your note.")
        return self.EDIT_DETAIL
    
    async def receive_detail_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        detail_text = update.message.text
        await self.handle_receive_detail_text(update, context, detail_text)
        self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def handle_receive_detail_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, detail_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['note_idx']
        response_text = await self.client.save_detail(chat_id, note_idx, detail_text)
        await update.message.reply_text(response_text)
