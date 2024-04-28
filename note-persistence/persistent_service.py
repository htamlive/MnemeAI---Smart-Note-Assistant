from typing import List
from reminder import Reminder


# This class serves as an interface for all the persistent services that will be implemented.
# Design for extension in the future.
class ReminderPersistentService:
    def store_reminder(self, reminder: Reminder):
        pass

    def get_reminders(self, gmail: str) -> List[Reminder]:
        pass

    def delete_reminder(self, gmail: str, id: str):
        pass

    def update_reminder(self, reminder: Reminder):
        pass
