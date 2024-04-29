from client import Client
from ..modify_note_conversation import EditNoteDetailConversation

class EditReminderDetailConversation(EditNoteDetailConversation):
    def __init__(self, EDIT_DETAIL: int, client: Client, debug: bool = True) -> None:
        super().__init__(EDIT_DETAIL, client, debug)

    async def client_save_detail(self, chat_id: int, idx: int) -> str:
        return await self.client.get_reminder_content(chat_id, idx)
    