from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from ._command_conversation import CommandConversation
from client import TelegramClient

class PromptingConversation(CommandConversation):
    def __init__(self, PROMPTING: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.PROMPTING = PROMPTING
        self._states = []
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            chat_id = update.message.chat_id
            prompt_text = ' '.join(context.args)
        
            response_text, next_state = await self.client.process_prompt(chat_id, prompt_text)

            if(self.debug):
                await update.message.reply_text(response_text)

            print(f'Next state: {next_state}')
            return next_state


        await update.message.reply_text("Oh, what's on your mind? Use /ah <prompt> to get started.")
        return None
    