
from bot.telegram.utils import check_data_requirement
from client import TelegramClient
from telegram.ext import CallbackQueryHandler

from llm.models import UserData

from ..note_conversation._view_notes_conversation import ViewNotesConversation
from bot.telegram.telegram_pages import NotePages, ReminderPages
from bot.telegram.ui_templates import get_reminder_option_keyboard, render_html_reminder_detail
from config import REMINDER_PAGE_CHAR, PAGE_DELIMITER, DETAIL_REMINDER_CHAR
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from client import TelegramClient

class ViewRemindersConversation(ViewNotesConversation):
    def __init__(self, VIEW_REMINDER: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(VIEW_REMINDER, EDIT_TITLE, EDIT_DETAIL, client, debug)

        self.previewing_pages: ReminderPages = self.init_reviewing_pages()

        self._states = [
            CallbackQueryHandler(self._preview_detail_callback, pattern=f'^{DETAIL_REMINDER_CHAR}{PAGE_DELIMITER}'),
            CallbackQueryHandler(self.previewing_pages._preview_page_callback, pattern=f'^{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}')
            ]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        success, message_text = check_data_requirement(context)

        if not success:
            await update.message.reply_text(message_text)
            return ConversationHandler.END

        await self.previewing_pages.show_preview_page(update, context)
        return self.VIEW_ITEMS

    def init_reviewing_pages(self) -> NotePages:
        return ReminderPages(self.client)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx)

    def share_preview_page_callback(self) -> CallbackQueryHandler:
        return CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern=f'^{REMINDER_PAGE_CHAR}{PAGE_DELIMITER}')

    async def client_get_content(self, context, chat_id: str, token: str) -> str:

        user_data = context.user_data['user_system_data']

        title, description, due = await self.client.get_reminder_content(UserData(chat_id=chat_id, reminder_token=token, timezone=user_data.timezone))
        html_render = render_html_reminder_detail(due, title, description)
        return html_render

    def update_review_message_tracker(self, context, message_id, text_html, token) -> dict:
        context.user_data['prev_review_message'] = {
            'message_id': message_id,
            'text_html': text_html,
            'reminder_token': token
        }

