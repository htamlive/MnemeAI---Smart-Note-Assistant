from telegram import (
    Update, CallbackQuery
)
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._modify_note_conversation import ModifyNoteConversation

from client import Client


class EditNoteTitleConversation(ModifyNoteConversation):
    def __init__(self, EDIT_TITLE: int, client: Client, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.EDIT_TITLE = EDIT_TITLE
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_title_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        note_idx = query.data.split('@')[1]
        
        context.user_data['item_idx'] = note_idx
        await query.message.reply_text("Please send me the new title of your note.")
        
        return self.EDIT_TITLE
    
    async def receive_title_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        title_text = update.message.text
        await self.handle_receive_title_text(update, context, title_text)

        self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def handle_receive_title_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['item_idx']

        response_text = await self.save_title(chat_id, note_idx, title_text)
        await update.message.reply_text(response_text)

    async def save_title(self, chat_id: int, note_idx: int, title_text: str) -> str:
        return await self.client_save_title(chat_id, note_idx, title_text)
    
    async def client_save_title(self, chat_id: int, note_idx: int, title_text: str) -> str:
        response_text = await self.client.save_note_title(chat_id, note_idx, title_text)
        return response_text