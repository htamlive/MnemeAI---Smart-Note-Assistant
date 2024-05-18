from bot.telegram.utils import check_data_requirement
from client import TelegramClient
from ...note_conversation.modify_note_conversation._edit_note_title_conversation import EditNoteTitleConversation

from telegram.ext import CallbackContext

class EditReminderTitleConversation(EditNoteTitleConversation):
    def __init__(self, EDIT_TITLE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(EDIT_TITLE, client, debug)

    async def client_save_title(self, chat_id: int, idx: int, title: str) -> str:
        return await self.client.save_reminder_title(chat_id, idx, title)

    def check_data_requirement(self, context) -> tuple:
        return check_data_requirement(context)