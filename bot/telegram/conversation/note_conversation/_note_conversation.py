from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from .._command_conversation import CommandConversation
from client import TelegramClient

class NoteConversation(CommandConversation):
    def __init__(self, NOTE_TEXT: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.NOTE_TEXT = NOTE_TEXT
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_note_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            note_text = ' '.join(context.args)
            await self.handle_receive_note_text(update, context, note_text)
            return ConversationHandler.END

        await update.message.reply_text("Please send me the text of your note.")
        return self.NOTE_TEXT
    
    async def receive_note_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        note_text = update.message.text
        await self.handle_receive_note_text(update, context, note_text)
        return ConversationHandler.END
    
    async def handle_receive_note_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_text: str) -> None:
        chat_id = update.message.chat_id
        response_text = await self.client.save_note(chat_id, note_text)
        await update.message.reply_text(response_text)
