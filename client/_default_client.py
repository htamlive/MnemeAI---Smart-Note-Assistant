from telegram.ext import CallbackContext
from telegram import Update
from test import pagination_test_data

class DefaultClient:
    def __init__(self) -> None:
        import dotenv
        import os

        dotenv.load_dotenv()
        self.TELEBOT_TOKEN = os.getenv

        self.api_url = f'https://api.telegram.org/bot{self.TELEBOT_TOKEN}/'
        # https://core.telegram.org/bots/api




    async def save_note(self, note_text) -> str:
        return f'Note saved: {note_text}'
    
    async def save_remind(self, remind_text) -> str:
        return f'Remind saved: {remind_text}'
    
    async def user_subscribe(self, chat_id):
        pass
        
    
    def get_jobs_from_start(self, update: Update) -> list:

        async def notify_assignees(context: CallbackContext) -> None:
            # await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello')
            print('sent message')

        # (function, interval in seconds)
        return [
            # (notify_assignees, 5)
        ]
    
    def get_note_content_at_page(self, page) -> str:
        title = pagination_test_data[page]['title']
        description = pagination_test_data[page]['description']

        return f'{title}\n\n{description}'