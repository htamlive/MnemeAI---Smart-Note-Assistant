from telegram_bot_pagination import InlineKeyboardPaginator
from telegram import InlineKeyboardButton

def create_preview_pages(num_pages: int, page_idx: int) -> InlineKeyboardPaginator:
    return InlineKeyboardPaginator(
                num_pages,
                current_page=page_idx,
                data_pattern='p#{page}'
            )

def create_preview_pages_json(chat_id: int, inital_text: str, num_pages: int, page_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': inital_text,
        'reply_markup': create_preview_pages(num_pages, page_idx).markup,
        'parse_mode': 'Markdown'
    }


def get_note_option_keyboard(note_idx: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'edit_note_title@{note_idx}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'edit_note_detail@{note_idx}'),
            InlineKeyboardButton('Delete', callback_data=f'delete_note@{note_idx}')
        ],
        [InlineKeyboardButton('Back', callback_data='back')]
    ]
    return keyboard

def get_reminder_option_keyboard(reminder_idx: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'edit_reminder_title@{reminder_idx}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'edit_reminder_detail@{reminder_idx}'),
            InlineKeyboardButton('Edit Time', callback_data=f'edit_reminder_time@{reminder_idx}'),
            InlineKeyboardButton('Delete', callback_data=f'delete_reminder@{reminder_idx}')
        ],
        [InlineKeyboardButton('Back', callback_data='back')]
    ]
    return keyboard

def get_delete_note_confirmation_keyboard(note_idx: str) -> list:
    keyboard = [
        [InlineKeyboardButton("Yes, delete it", callback_data=f'confirm_delete_note@{note_idx}')],
        [InlineKeyboardButton("No, go back", callback_data=f'cancel_delete_note@{note_idx}')]
    ]
    return keyboard

def get_delete_reminder_confirmation_keyboard(reminder_idx: str) -> list:
    keyboard = [
        [InlineKeyboardButton("Yes, delete it", callback_data=f'confirm_delete_reminder@{reminder_idx}')],
        [InlineKeyboardButton("No, go back", callback_data=f'cancel_delete_reminder@{reminder_idx}')]
    ]
    return keyboard