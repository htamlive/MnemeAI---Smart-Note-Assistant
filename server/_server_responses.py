import dotenv
import os
from bot.telegram import create_note_pages_json
import requests
from config import *


dotenv.load_dotenv()

TOKEN = os.getenv('TELEBOT_TOKEN')

base_url = f'https://api.telegram.org/bot{TOKEN}/'

def show_note_pages(chat_id: str, text: str, num_pages: int, page_idx: int):
    url = f'{base_url}sendMessage'
    
    payload = create_note_pages_json(chat_id, text, num_pages, page_idx)

    response = requests.post(url, json=payload)

    ret_response = {
            "ok": True,
            'result': {
                'response_text': 'Prompt received',
                'next_state': VIEW_NOTES,
            }
        }
    
    return response.json(), ret_response