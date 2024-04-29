import threading

from models.reminder import Reminder
from typing import List
from models.configuration import Configuration
from postgres.factory import PostgresServiceFactory

mock_reminders: List[Reminder] = [
    Reminder(
        chat_id="jdbsvbjvdfhvacsdhsv",
        id=1,
        title="TestA",
        description="TestA",
        due_date="2022-01-01T00:00:00",
    ),
    Reminder(
        chat_id="dshdcbsvbshjvdsvhsdvsvsvbdsvsvhdsv",
        id=1,
        title="TestB",
        description="TestB",
        due_date="2022-01-01T00:00:00",
    ),
    Reminder(
        chat_id="jdbsvbjvdfhvacsdhsv",
        id=2,
        title="TestA",
        description="TestA",
        due_date="2022-01-01T00:00:00",
    ),
]

flag = threading.Event()
def main():
    postgres_factory = PostgresServiceFactory(flag=flag, config=Configuration.default())

    (storage_consumer, movement_consumer, delivery_consumer) = (
        postgres_factory.storage_service(),
        postgres_factory.movement_service(),
        postgres_factory.delivery_service(),
    )

    # Run the movement service and delivery service in separate threads
    movement_consumer.start()
    delivery_consumer.start()

    # Insertion works fine
    for reminder in mock_reminders:
        storage_consumer.store_reminder(reminder)

    # Sleep for 1 minute
    import time

    time.sleep(60)

    flag.set()


main()
