from bot.telegram.utils import check_data_requirement
from client import TelegramClient
from ...note_conversation.modify_note_conversation._edit_note_detail_conversation import EditNoteDetailConversation
from telegram.ext import CallbackContext

class EditReminderDetailConversation(EditNoteDetailConversation):
    def __init__(self, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(EDIT_DETAIL, client, debug)

    def check_data_requirement(self, context: CallbackContext.DEFAULT_TYPE) -> tuple:
        return check_data_requirement(context)

    async def client_save_detail(self, chat_id: int, token: str, detail_text: str) -> str:
        return await self.client.save_reminder_detail(chat_id, token, detail_text)
    