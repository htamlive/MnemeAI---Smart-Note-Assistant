import datetime
from telegram_bot_pagination import InlineKeyboardPaginator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Patterns, REMINDER_PAGE_CHAR, NOTE_PAGE_CHAR, PAGE_DELIMITER, DETAIL_REMINDER_CHAR

def create_preview_pages(num_pages: int, page_idx: int, pattern = NOTE_PAGE_CHAR + '#{page}') -> InlineKeyboardPaginator:
    return InlineKeyboardPaginator(
                num_pages,
                current_page=page_idx,
                data_pattern=pattern
            )

def create_preview_note_pages_json(chat_id: int, inital_text: str, num_pages: int, page_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': inital_text,
        'reply_markup': create_preview_pages(num_pages, page_idx).markup,
        'parse_mode': 'HTML'
    }

def create_preview_reminder_pages_json(chat_id: int, inital_text: str, num_pages: int, page_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': inital_text,
        'reply_markup': create_preview_pages(num_pages, page_idx, pattern= REMINDER_PAGE_CHAR + '#{page}').markup,
        'parse_mode': 'HTML'
    }

def get_note_option_keyboard(note_idx: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'{Patterns.EDIT_NOTE_TITLE.value}{note_idx}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'{Patterns.EDIT_NOTE_DETAIL.value}{note_idx}'),
            InlineKeyboardButton('Delete', callback_data=f'{Patterns.DELETE_NOTE.value}{note_idx}')
        ],
        [InlineKeyboardButton('Back', callback_data='back')]
    ]
    return keyboard

def get_reminder_option_keyboard(reminder_token: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'{Patterns.EDIT_REMINDER_TITLE.value}{reminder_token}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'{Patterns.EDIT_REMINDER_DETAIL.value}{reminder_token}'),
            InlineKeyboardButton('Edit Time', callback_data=f'{Patterns.EDIT_REMINDER_TIME.value}{reminder_token}'),
            InlineKeyboardButton('Delete', callback_data=f'{Patterns.DELETE_REMINDER.value}{reminder_token}')
        ],
        [InlineKeyboardButton('Back', callback_data='back')]
    ]
    return keyboard


def get_delete_note_confirmation_keyboard(note_idx: str) -> list:
    print("note_idx", note_idx)
    keyboard = [
        [InlineKeyboardButton("Yes, delete it", callback_data=f'{Patterns.CONFIRM_DELETE_NOTE.value}{note_idx}')],
        [InlineKeyboardButton("No, go back", callback_data=f'{Patterns.CANCEL_DELETE_NOTE.value}{note_idx}')]
    ]
    return keyboard

def get_delete_reminder_confirmation_keyboard(reminder_idx: str) -> list:
    print("reminder_idx", reminder_idx)
    keyboard = [
        [InlineKeyboardButton("Yes, delete it", callback_data=f'{Patterns.CONFIRM_DELETE_REMINDER.value}{reminder_idx}')],
        [InlineKeyboardButton("No, go back", callback_data=f'{Patterns.CANCEL_DELETE_REMINDER.value}{reminder_idx}')]
    ]
    return keyboard

def create_review_note_json(chat_id: int, note_text: str, note_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': note_text,
        'reply_markup': InlineKeyboardMarkup(get_note_option_keyboard(note_idx)),
        'parse_mode': 'HTML'
    }

def create_review_reminder_json(chat_id: int, reminder_text: str, reminder_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': reminder_text,
        'reply_markup': InlineKeyboardMarkup(get_reminder_option_keyboard(reminder_idx)),
        'parse_mode': 'HTML'
    }

def show_reminders_list(chat_id: int, titles: list, reminder_tokens: list, next_page_token: str, cur_page_token: str | None = None) -> dict:
    keyboards = []
    for title, token in zip(titles, reminder_tokens):
        keyboards.append([InlineKeyboardButton(title, callback_data=f'{DETAIL_REMINDER_CHAR}{PAGE_DELIMITER}{token}')])
    
    if next_page_token:
        keyboards.append([InlineKeyboardButton('Show more', callback_data=f'{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}{next_page_token}')])

    count_items = len(titles)

    text = 'Here are your reminders:\n'
    if cur_page_token is None:
        if count_items > 1:
            text = 'Here are your reminders:\n'
        elif count_items == 1:
            text = 'Here is your reminder:\n'
        elif count_items == 0:
            text = 'There is no reminder yet'
    else:
        # show text for more reminders
        text = 'Here are more of your reminders:\n'

    return {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': InlineKeyboardMarkup(keyboards),
        'parse_mode': 'HTML'
    }

def show_notes_list(chat_id: int, titles: list, note_tokens: list, starting_point: str = None) -> dict:
    keyboards = []
    for title, token in zip(titles, note_tokens):
        keyboards.append([InlineKeyboardButton(title, callback_data=f'{NOTE_PAGE_CHAR}{PAGE_DELIMITER}{token}')])

    if starting_point:
        keyboards.append([InlineKeyboardButton('show more', callback_data=f'{NOTE_PAGE_CHAR}{PAGE_DELIMITER}{starting_point}')])

    count_items = len(titles)

    text = 'Here are your notes:\n'
    if count_items > 1:
        text = 'Here are your notes:\n'
    elif count_items == 1:
        text = 'Here is your note:\n'
    elif count_items == 0:
        text = 'There is no note yet'

    return {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': InlineKeyboardMarkup(keyboards),
        'parse_mode': 'HTML'
    }


def render_html_reminder_detail(due: datetime, title: str, description: str) -> str:
    html_render = \
        "<b>📌 YOUR REMINDERS:</b>\n" \
        "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦\n\n<b>"\
        f"🔹 <i>{title}</i></b>\n"\
        f"\n📝\n{description}\n"\
        f"\n⏰\n{due}"

    return html_render

