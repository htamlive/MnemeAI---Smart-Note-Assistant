from client import Client
from ..modify_note_conversation import EditNoteTitleConversation

class EditReminderTitleConversation(EditNoteTitleConversation):
    def __init__(self, EDIT_TITLE: int, client: Client, debug: bool = True) -> None:
        super().__init__(EDIT_TITLE, client, debug)

    async def client_save_title(self, chat_id: int, idx: int, title: str) -> None:
        await self.client.save_reminder_title(chat_id, idx, title)