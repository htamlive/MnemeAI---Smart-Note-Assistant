from typing import List

from persistent_service import ReminderPersistentService
from reminder import Reminder


class StorageConsumer:
    def __init__(self, db_service: ReminderPersistentService) -> None:
        self.__service = db_service

    def store_reminder(self, reminder: Reminder):
        self.__service.store_reminder(reminder)

    def get_reminders(self, gmail: str) -> List[Reminder]:
        return self.__service.get_reminders(gmail)

    def delete_reminder(self, gmail: str, id: str):
        self.__service.delete_reminder(gmail, id)

    def update_reminder(self, reminder: Reminder):
        self.__service.update_reminder(reminder)
