from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from llm.models import UserData
from llm._tools import show_notes_list
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

            user_data: UserData = UserData()

            user_data.chat_id = chat_id
            if('prev_review_message' in context.user_data):
                data = context.user_data['prev_review_message']
                user_data.reminder_token = data.get('reminder_token', None)
                user_data.note_token = data.get('note_token', None)
        

            # await add_note(user_data, "Julia is very good", "Julia is very good")

            await show_notes_list(user_data)

            return ConversationHandler.END
            
            response_text, next_state = await self.client.process_prompt(user_data, prompt_text)

            if(self.debug):
                await update.message.reply_text(response_text)

            # print(f'Next state: {next_state}')
            return next_state


        await update.message.reply_text("Oh, what's on your mind? Use /ah <prompt> to get started.")
        return None
    