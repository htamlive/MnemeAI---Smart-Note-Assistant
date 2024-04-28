from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._command_conversation import CommandConversation
from client import Client

class PromptingConversation(CommandConversation):
    def __init__(self, PROMPTING: int, client: Client) -> None:
        self.client = client
        self.PROMPTING = PROMPTING
        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_prompt)]
        
    async def start_conservation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            note_text = ' '.join(context.args)
            await self.handle_receive_prompt_text(update, context, note_text)
            return ConversationHandler.END

        await update.message.reply_text("Oh, what's on your mind?")
        return self.PROMPTING
    
    async def receive_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        note_text = update.message.text
        return await self.handle_receive_prompt_text(update, context, note_text)
    
    async def handle_receive_prompt_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt_text: str) -> int:
        chat_id = update.message.chat_id
        response_text, next_state = await self.client.process_prompt(chat_id, prompt_text)

        if(self.debug):
            await update.message.reply_text(response_text)

        return next_state