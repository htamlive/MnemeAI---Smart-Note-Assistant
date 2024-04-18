from telegram import Update
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import ContextTypes, ConversationHandler

from ._command_conversation import CommandConversation


class NoteConversation(CommandConversation):
    def __init__(self, NOTE_TEXT: int) -> None:
        self.NOTE_TEXT = NOTE_TEXT
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_note_text)]
        
    async def start_conservation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            note_text = ' '.join(context.args)
            await self.receive_note_text(update, context, note_text)
            return ConversationHandler.END

        await update.message.reply_text("Please send me the text of your note.")
        return self.NOTE_TEXT
    
    async def receive_note_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        note_text = update.message.text
        await self.receive_note_text(update, context, note_text)
        return ConversationHandler.END
    
    async def receive_note_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_text: str) -> None:
        await update.message.reply_text(f"Note saved: {note_text}")
