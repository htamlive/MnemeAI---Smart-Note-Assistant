from telegram import Update, Message
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from .._command_conversation import CommandConversation
from client import TelegramClient

class RequestNotionDBConversation(CommandConversation):
    def __init__(self, NOTION_REQ_DB: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.NOTION_REQ_DB = NOTION_REQ_DB

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_user_data)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            remind_text = ' '.join(context.args)
            await self._handle_receive_data(update, context, remind_text)
            return ConversationHandler.END
        await update.message.reply_text("Please send me the database URL or database ID.")
        return self.NOTION_REQ_DB
    
    async def receive_user_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_text = update.message.text
        message = await update.message.reply_text("Got it! Please wait a moment.")
        await self._handle_receive_data(update, context, user_text, message)
        return ConversationHandler.END
    

    async def _handle_receive_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, message: Message) -> None:
        chat_id = update.message.chat_id
        response_text = await self.client.handle_receive_notion_database_token(chat_id, data)
        
        await message.edit_text(response_text)