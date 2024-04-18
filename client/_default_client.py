class DefaultClient:
    def __init__(self) -> None:
        pass

    async def save_note(self, note_text) -> str:
        return f'Note saved: {note_text}'
    
    async def save_remind(self, remind_text) -> str:
        return f'Remind saved: {remind_text}'