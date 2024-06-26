from telegram import Message, Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from bot.telegram.utils import check_data_requirement
from llm.models import UserData
from .._command_conversation import CommandConversation
from client import TelegramClient

class RemindConversation(CommandConversation):
    def __init__(self, REMIND_TEXT: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.REMIND_TEXT = REMIND_TEXT

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_remind_text)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        success, message = check_data_requirement(context)

        if not success:
            await update.message.reply_text(message)
            return ConversationHandler.END

        if(context.args):
            remind_text = ' '.join(context.args)
            await self._handle_receive_remind_text(update, context, remind_text)
            return ConversationHandler.END
        await update.message.reply_text("Please send me the details of the reminder.")
        return self.REMIND_TEXT
    
    async def receive_remind_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        remind_text = update.message.text
        await self._handle_receive_remind_text(update, context, remind_text)
        return ConversationHandler.END
    

    async def _handle_receive_remind_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, remind_text: str) -> None:

        message = await update.message.reply_text("Got it! Please wait a moment.")
        response_text = await self.client.save_remind(
            user_data=context.user_data['user_system_data'],
            remind_text=remind_text
            )
        
        await message.edit_text(response_text)