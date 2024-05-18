from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from bot.telegram.utils import check_data_requirement
from llm.models import UserData
from ._command_conversation import CommandConversation
from client import TelegramClient

class PromptingConversation(CommandConversation):
    def __init__(self, PROMPTING: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.PROMPTING = PROMPTING
        self._states = []
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:   
        success, message = check_data_requirement(context)

        if not success:
            await update.message.reply_text(message)
            return ConversationHandler.END

        if(context.args):
            prompt_text = ' '.join(context.args)

            user_data: UserData = context.user_data.get('user_system_data', None)

            if(user_data is None):
                await update.message.reply_text("Please use /start to get started.")
                return None

            if('prev_review_message' in context.user_data):
                data = context.user_data['prev_review_message']
                user_data.reminder_token = data.get('reminder_token', None)
                user_data.note_token = data.get('note_token', None)
            

        

            # await add_note(user_data, "Julia is very good", "Julia is very good")

            # await show_notes_list(user_data)
            #print location
            # print(update.message.location)
            # print(await update_timezone_utc(user_data, 7))
            # res = await retrieve_knowledge_from_notes(user_data, prompt="Get everything about Julia")
            # return ConversationHandler.END

            message = await update.message.reply_text("Got it! Please wait a moment.")
            
            response_text, next_state = await self.client.process_prompt(user_data, prompt_text)

            if(self.debug):
                await message.edit_text(response_text)

            # print(f'Next state: {next_state}')
            return next_state


        await update.message.reply_text("Oh, what's on your mind? Use /ah <prompt> to get started.")
        return None
    