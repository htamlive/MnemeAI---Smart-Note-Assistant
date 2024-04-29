from flask import Flask, request
import dotenv
import os
import requests
import time
from config import *
from server import show_note_pages
from test import pagination_test_data

dotenv.load_dotenv()

TOKEN = os.getenv('TELEBOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

base_url = f'https://api.telegram.org/bot{TOKEN}/'

# response = send_message(CHAT_ID, 'Hello, World!').json()

# message_id = response['result']['message_id']
# chat_id = response['result']['chat']['id']

# time.sleep(5)

# response = delete_message(chat_id, message_id).json()
# print(response)


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/prompt', methods=['POST'])
def prompt():
    data = request.json

    chat_id = data['chat_id']
    prompt_text = data['prompt_text']

    # This is a very simple way to handle the prompt
    if('show note' in prompt_text):

        initial_text = f'{pagination_test_data[0]["title"]}\n{pagination_test_data[0]["description"]}'

        response, ret_response = show_note_pages(chat_id, initial_text, len(pagination_test_data), 1)

        print(f'{response=}')

    else:
        ret_response = {
            "ok": True,
            'result': {
                'response_text': 'Prompt received',
                # This means that the next state is the same as the current state
                'next_state': None,
            }
        }

    return ret_response


if __name__ == '__main__':
    app.run(debug=True)


