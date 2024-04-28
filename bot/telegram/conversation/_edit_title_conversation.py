from telegram import (
    Update, CallbackQuery
)
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._edit_note_conversation import EditNoteConversation

from client import Client


class EditTileConversation(EditNoteConversation):
    def __init__(self, EDIT_TITLE: int, client: Client, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.EDIT_TITLE = EDIT_TITLE
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_title_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        note_idx = query.data.split('@')[1]
        
        context.user_data['note_idx'] = note_idx
        await query.message.reply_text("Please send me the new title of your note.")
        
        return self.EDIT_TITLE
    
    async def receive_title_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        title_text = update.message.text
        await self.handle_receive_title_text(update, context, title_text)

        self.on_finish_edit(update, context)

        return ConversationHandler.END
    
    async def handle_receive_title_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title_text: str) -> None:
        chat_id = update.message.chat_id
        note_idx = context.user_data['note_idx']

        response_text = await self.client.save_title(chat_id, note_idx, title_text)
        await update.message.reply_text(response_text)
