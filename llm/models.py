class UserData:
    def __init__(self, chat_id: int | None = None, reminder_token: str | None = None, note_token: str | None = None, timezone: str | None = None) -> None:
        self.chat_id = chat_id
        self.reminder_token = reminder_token
        self.note_token = note_token
        self.timezone = timezone
