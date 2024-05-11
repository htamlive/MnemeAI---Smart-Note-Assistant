
from client import TelegramClient
from telegram.ext import CallbackQueryHandler

from ..note_conversation._view_notes_conversation import ViewNotesConversation
from bot.telegram.telegram_pages import NotePages, ReminderPages
from bot.telegram.ui_templates import get_reminder_option_keyboard
from config import REMINDER_PAGE_CHAR, PAGE_DELIMITER, DETAIL_REMINDER_CHAR
from telegram import Update
from telegram.ext import ContextTypes

from client import TelegramClient

class ViewRemindersConversation(ViewNotesConversation):
    def __init__(self, VIEW_REMINDER: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(VIEW_REMINDER, EDIT_TITLE, EDIT_DETAIL, client, debug)

        self.previewing_pages: ReminderPages = self.init_reviewing_pages()

        self._states = [
            CallbackQueryHandler(self._preview_detail_callback, pattern=f'^{DETAIL_REMINDER_CHAR}{PAGE_DELIMITER}'),
            ]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await self.previewing_pages.show_preview_page(update, context)
        return self.VIEW_ITEMS

    def init_reviewing_pages(self) -> NotePages:
        return ReminderPages(self.client)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx)

    def share_preview_page_callback(self) -> CallbackQueryHandler:
        return CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern=f'^{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}')

    async def client_get_content(self, chat_id: int, idx: int) -> str:
        return await self.client.get_reminder_content(chat_id, idx)


