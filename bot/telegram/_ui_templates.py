from telegram_bot_pagination import InlineKeyboardPaginator

def create_note_pages(num_pages: int, page_idx: int) -> InlineKeyboardPaginator:
    return InlineKeyboardPaginator(
                num_pages,
                current_page=page_idx,
                data_pattern='p#{page}'
            )

def create_note_pages_json(chat_id: int, inital_text: str, num_pages: int, page_idx: int) -> str:
    return {
        'chat_id': chat_id,
        'text': inital_text,
        'reply_markup': create_note_pages(num_pages, page_idx).markup,
        'parse_mode': 'Markdown'
    }