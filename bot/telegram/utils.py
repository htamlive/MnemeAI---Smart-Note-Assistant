import base64
from typing import Tuple

from llm.models import UserData

def get_hidden_url_html(tokens: list) -> str:
    encoded_data = b'\0'.join([token.encode() for token in tokens])
    url = f'tg://btn/{base64.urlsafe_b64encode(encoded_data).decode()}'

    res = f'<a href="{url}">\u200b</a>'
    return res

def extract_hidden_url_data(url: str) -> list:
    encoded_data = url.split('tg://btn/')[1]
    raw_data = base64.urlsafe_b64decode(encoded_data.encode()).split(b'\0')
    return [data.decode() for data in raw_data]

def extract_hidden_tokens(entities) -> list:
    for entity in entities:
        if entity.type == 'text_link':
            return extract_hidden_url_data(entity.url)
        
    raise Exception('No text link found')


def check_data_requirement(context, check_timezone = True) ->Tuple[bool, str]:
    if('user_system_data' not in context.user_data):
        return False, 'Please initialize your user data first with /start'
    
    user_data : UserData = context.user_data['user_system_data']

    if(check_timezone and not user_data.timezone):
        return False, 'Please set your timezone first with /timezone'
    
    return True, 'OK'