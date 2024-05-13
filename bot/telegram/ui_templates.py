from telegram_bot_pagination import InlineKeyboardPaginator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Patterns, REMINDER_PAGE_CHAR, NOTE_PAGE_CHAR

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

def get_reminder_option_keyboard(reminder_idx: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'{Patterns.EDIT_REMINDER_TITLE.value}{reminder_idx}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'{Patterns.EDIT_REMINDER_DETAIL.value}{reminder_idx}'),
            InlineKeyboardButton('Edit Time', callback_data=f'{Patterns.EDIT_REMINDER_TIME.value}{reminder_idx}'),
            InlineKeyboardButton('Delete', callback_data=f'{Patterns.DELETE_REMINDER.value}{reminder_idx}')
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
