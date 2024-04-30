import dotenv
import os
from bot.telegram.ui_templates import create_preview_note_pages_json, create_review_note_json, create_review_reminder_json
import requests
from config import *


dotenv.load_dotenv()

TOKEN = os.getenv('TELEBOT_TOKEN')

base_url = f'https://api.telegram.org/bot{TOKEN}/'

def example_send_message(chat_id: str, text: str) -> requests.Response:
    

    url = f'{base_url}sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': text,
        # 'reply_markup': {
        #     'inline_keyboard': [
        #         [{
        #             'text': 'Button 1', 
        #             'callback_data': '1'
        #             }], 
        #         [{'text': 'Button 2', 'callback_data': '2'}]  
        #     ]
        # }
    }

    return requests.post(url, json=payload)

def delete_message(chat_id: str, message_id: int) -> requests.Response:
    url = f'{base_url}deleteMessage'
    
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    
    return requests.post(url, json=payload)

def show_note_pages(chat_id: str, text: str, num_pages: int, page_idx: int):
    '''
        page_idx is 1-based index
    '''
    url = f'{base_url}sendMessage'
    
    payload = create_preview_note_pages_json(chat_id, text, num_pages, page_idx)

    response = requests.post(url, json=payload)

    ret_response = {
            "ok": True,
            'result': {
                'response_text': 'Here are the notes.',
                'next_state': VIEW_NOTES,
            }
        }
    
    return response.json(), ret_response

def show_review_note_page(chat_id: str, note_idx: str):
    url = f'{base_url}sendMessage'
    
    payload = create_review_note_json(chat_id, note_idx)

    response = requests.post(url, json=payload)

    ret_response = {
            "ok": True,
            'result': {
                'response_text': 'Here is the note.',
                'next_state': VIEW_NOTES,
            }
        }
    
    return response.json(), ret_response

def show_review_reminder_page(chat_id: str, reminder_idx: str):
    url = f'{base_url}sendMessage'
    
    payload = create_review_reminder_json(chat_id, reminder_idx)

    response = requests.post(url, json=payload)

    ret_response = {
            "ok": True,
            'result': {
                'response_text': 'Here is the reminder.',
                'next_state': VIEW_REMINDERS,
            }
        }
    
    return response.json(), ret_response
