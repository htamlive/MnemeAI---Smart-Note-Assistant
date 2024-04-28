from flask import Flask
import dotenv
import os
import requests
import time

dotenv.load_dotenv()

TOKEN = os.getenv('TELEBOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

base_url = f'https://api.telegram.org/bot{TOKEN}/'

def send_message(chat_id: str, text: str) -> requests.Response:
    

    url = f'{base_url}sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard': [
                [{
                    'text': 'Button 1', 
                    'callback_data': '1'
                    }], 
                [{'text': 'Button 2', 'callback_data': '2'}]  
            ]
        }
    }

    return requests.post(url, json=payload)


def delete_message(chat_id: str, message_id: int) -> requests.Response:
    url = f'{base_url}deleteMessage'
    
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    
    return requests.post(url, json=payload)

response = send_message(CHAT_ID, 'Hello, World!').json()

message_id = response['result']['message_id']
chat_id = response['result']['chat']['id']

time.sleep(5)

response = delete_message(chat_id, message_id).json()
print(response)



