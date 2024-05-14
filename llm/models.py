class UserData:
    def __init__(self, chat_id: int | None = None, reminder_token: str | None = None):
        self.chat_id = chat_id
        self.reminder_token = reminder_token
