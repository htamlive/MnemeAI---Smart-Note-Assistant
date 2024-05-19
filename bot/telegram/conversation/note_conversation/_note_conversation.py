from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from bot.telegram.utils import check_data_requirement
from llm.models import UserData
from .._command_conversation import CommandConversation
from client import TelegramClient

class NoteConversation(CommandConversation):
    def __init__(self, NOTE_TEXT: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.NOTE_TEXT = NOTE_TEXT
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_note_text)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        success, message = check_data_requirement(context)

        if not success:
            await update.message.reply_text(message)
            return
        
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
        
        user_data = context.user_data['user_system_data']
        chat_id = update.effective_chat.id

        message = await update.message.reply_text("Got it! Please wait a moment.")
        response_text = await self.client.save_note(
            user_data=UserData(
                chat_id=chat_id,
                timezone=user_data.timezone
                ),
            note_text=note_text
            )
        await message.edit_text(response_text)
