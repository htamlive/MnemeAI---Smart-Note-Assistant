from telegram import Update, Message
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from .._command_conversation import CommandConversation
from client import TelegramClient

from deprecatedFunction import deprecated

class RequestNotionPageConversation(CommandConversation):
    def __init__(self, NOTION_REQ_PAGE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.NOTION_REQ_PAGE = NOTION_REQ_PAGE

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_user_data)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            remind_text = ' '.join(context.args)
            await self._handle_receive_data(update, context, remind_text)
            return ConversationHandler.END
        await update.message.reply_text("Please send me the page URL or page ID.")
        return self.NOTION_REQ_PAGE
    
    async def receive_user_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_text = update.message.text
        message = await update.message.reply_text("Got it! Please wait a moment.")
        await self._handle_receive_data(update, context, user_text, message)
        return ConversationHandler.END
    

    @deprecated
    async def _handle_receive_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token: str, message: Message) -> None:
        chat_id = update.message.chat_id
        # response_text = await self.client.handle_receive_notion_page_token(chat_id, token)
        response_text = "This function is deprecated"
        await message.edit_text(response_text)