from telegram import Update
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import ContextTypes, ConversationHandler
from ._command_conversation import CommandConversation

class RemindConversation(CommandConversation):
    def __init__(self, REMIND_TEXT: int) -> None:

        self.REMIND_TEXT = REMIND_TEXT

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_remind_text)]

    async def start_conservation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Please send me the details of the reminder.")
        return self.REMIND_TEXT
    
    async def receive_remind_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        remind_text = update.message.text
        await update.message.reply_text(f"remind set for: {remind_text}")
        return ConversationHandler.END