
from client import TelegramClient
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

from ._view_notes_conversation import ViewNotesConversation
from bot.telegram.telegram_pages import NotePages, ReminderPages
from bot.telegram.ui_templates import get_reminder_option_keyboard

from client import TelegramClient

def get_modifying_option_keyboard(note_idx: str) -> list:
    keyboard = [
        [
            InlineKeyboardButton('Edit Title', callback_data=f'edit_reminder_title@{note_idx}'),
            InlineKeyboardButton('Edit Detail', callback_data=f'edit_reminder_detail@{note_idx}'),
            InlineKeyboardButton('Delete', callback_data=f'delete_reminder@{note_idx}')
        ],
        [InlineKeyboardButton('Back', callback_data='back')]
    ]
    return keyboard

class ViewRemindersConversation(ViewNotesConversation):
    def __init__(self, VIEW_NOTES: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(VIEW_NOTES, EDIT_TITLE, EDIT_DETAIL, client, debug)

    def init_reviewing_pages(self) -> NotePages:
        return ReminderPages(self.client)
    
    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx)
    
    def share_preview_page_callback(self) -> CallbackQueryHandler:
        return CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern='^r#')
    
    def client_get_content(self, chat_id: int, idx: int) -> str:
        return self.client.get_reminder_content(chat_id, idx)


    