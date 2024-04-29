from telegram.ext import (
    CallbackContext, ConversationHandler
)
from telegram import Update
from test import pagination_test_data
import requests
from config import *    
from urllib.parse import quote


class DefaultClient:
    def __init__(self) -> None:
        import dotenv
        import os

        dotenv.load_dotenv()
        self.TELEBOT_TOKEN = os.getenv
        self.SERVER_URL = os.getenv('SERVER_URL')

        self.api_url = f'https://api.telegram.org/bot{self.TELEBOT_TOKEN}/'
        # https://core.telegram.org/bots/api

    async def user_subscribe(self, chat_id):
        pass

    async def save_note(self, chat_id, note_text) -> str:
        return f'Note saved: {note_text}'
    
    async def save_remind(self, chat_id, remind_text) -> str:
        return f'Remind saved: {remind_text}'
    
    #================= Note =================

    async def save_note_title(self, chat_id, note_idx, title_text):
        return f'Title saved: {title_text}'
    
    async def save_note_detail(self, chat_id, note_idx, detail_text):
        return f'Detail saved: {detail_text}'
    
    async def delete_note(self, chat_id, page) -> str:
        return f'Note deleted at page {page}'
    
    def get_note_content_at_page(self, chat_id, page) -> str:
        return self.get_note_content(chat_id, page)
    
    def extract_note_idx(self, note_idx_text) -> int:
        '''
        May use LLM to extract note index from text
        '''

        # this is 1-based index -> 0-based index
        return int(note_idx_text) - 1
    
    def get_note_content(self, chat_id, note_idx_text) -> str:

        # Remember to convert to 0-based index
        note_idx = self.extract_note_idx(note_idx_text)

        title = pagination_test_data[note_idx]['title']
        description = pagination_test_data[note_idx]['description']

        return f'<b>{title}</b>\n\n{description}'
    
    def get_total_note_pages(self) -> int:
        return len(pagination_test_data)
    
    #================= Reminder =================

    def extract_reminder_idx(self, reminder_idx_text) -> int:
        '''
        May use LLM to extract reminder index from text
        '''

        # this is 1-based index -> 0-based index
        return int(reminder_idx_text) - 1

    def get_reminder_content(self, chat_id, idx) -> str:
        reminder_indx = self.extract_reminder_idx(idx)

        title = pagination_test_data[reminder_indx]['title']
        description = pagination_test_data[reminder_indx]['description']
        time = pagination_test_data[reminder_indx]['time']

        html_render = f"<b>{title}</b> \n{time}\n\n{description}"

        return html_render
        # return f'{title} ' + '<a href="href="tg://bot_command?command=start" onclick="execBotCommand(this)">edit</a>' + '{time}{description}'

    async def get_reminder_content_at_page(self, chat_id, page) -> str:
        return self.get_reminder_content(chat_id, page)

    async def delete_reminder(self, chat_id, page) -> str:
        return self.delete_note(chat_id, page)

    async def save_reminder_title(self, chat_id, idx, title_text) -> str:
        pass

        
    async def save_reminder_detail(self, chat_id, idx, detail_text) -> str:
        return f'Detail saved: {detail_text}'

    async def save_reminder_time(self, chat_id, idx, time) -> str:
        return f'Time edited: {time}'
    
    def get_total_reminder_pages(self) -> int:
        return len(pagination_test_data)
    
    #================= Other =================

    async def process_prompt(self, chat_id, prompt_text) -> str:
        response = requests.post(f'{self.SERVER_URL}/prompt', json={'chat_id': chat_id, 'prompt_text': prompt_text}).json()

        print(response)

        return response['result']['response_text'], response['result']['next_state']
    
    def get_jobs_from_start(self, update: Update) -> list:

        async def notify_assignees(context: CallbackContext) -> None:
            # await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello')
            print('sent message')

        # (function, interval in seconds)
        return [
            # (notify_assignees, 5)
        ]
    