from datetime import datetime


class Reminder:
    def __init__(
        self, chat_id: str, id: int, title: str, description: str, due_date: datetime
    ) -> None:
        self.chat_id = chat_id
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date

    def to_json(self) -> dict:
        return {
            "chat_id": self.chat_id,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
        }

    def __str__(self) -> str:
        return f"{self.title}: {self.description} at {self.due_date.isoformat()}"

    @staticmethod
    def from_json(json: dict) -> "Reminder":
        return Reminder(
            json["chat_id"],
            json["id"],
            json["title"],
            json["description"],
            datetime.fromisoformat(json["due_date"]),
        )
