from telegram import Update, Message
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._command_conversation import CommandConversation
from client import TelegramClient

class QueryKnowledgeConversation(CommandConversation):
    def __init__(self, QUERY_KNOWLEDGE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.QUERY_KNOWLEDGE = QUERY_KNOWLEDGE

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_user_query)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not 'user_system_data' in context.user_data:
            await update.message.reply_text("Please start the bot first with /start")
            return

        if(context.args):
            query = ' '.join(context.args)
            await self._handle_receive_query(update, context, query)
            return ConversationHandler.END
        await update.message.reply_text("Please send me your query.")
        return self.QUERY_KNOWLEDGE
    
    async def receive_user_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_text = update.message.text
        
        await self._handle_receive_query(update, context, user_text)
        return ConversationHandler.END
    

    async def _handle_receive_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
        

        message = await update.message.reply_text("Got it! This may take a while. Please wait a moment.")
        response_text = await self.client.receive_prompt_for_knowledge_retrieval(context.user_data['user_system_data'], token)
        
        await message.edit_text(response_text)