import threading
from typing import List
from models.reminder import Reminder

# This class serves as an interface for all the persistent services that will be implemented.
class ReminderPersistentService:
    def store_reminder(self, reminder: Reminder):
        pass

    def get_reminders(self, chat_id: str) -> List[Reminder]:
        pass

    def delete_reminder(self, chat_id: str, id: str):
        pass

    def update_reminder(self, reminder: Reminder):
        pass


# An interface for service that delivers reminders to the client
class ReminderDeliveryService(threading.Thread):
    def deliver_reminder(self) -> bool:
        pass


# An interface for serice that moves available reminders
# to the delivery reminder table from the reminder table
class MovementService(threading.Thread):
    # True if there are reminders to move, False otherwise
    def move_pending_reminder(self) -> bool:
        pass

class ReminderDeliveryFactory:
    def storage_service(self) -> ReminderPersistentService:
        pass

    def movement_service(self) -> MovementService:
        pass

    def delivery_service(self) -> ReminderDeliveryService:
        pass
