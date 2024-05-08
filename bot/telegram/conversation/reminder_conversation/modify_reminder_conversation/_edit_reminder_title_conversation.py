from client import TelegramClient
from ...note_conversation.modify_note_conversation._edit_note_title_conversation import EditNoteTitleConversation

class EditReminderTitleConversation(EditNoteTitleConversation):
    def __init__(self, EDIT_TITLE: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(EDIT_TITLE, client, debug)

    async def client_save_title(self, chat_id: int, idx: int, title: str) -> None:
        await self.client.save_reminder_title(chat_id, idx, title)