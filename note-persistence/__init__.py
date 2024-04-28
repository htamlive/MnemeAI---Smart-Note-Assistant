from storage_injector import PostgresInjectorImpl, StorageInjector
from storage_consumer import StorageConsumer
from reminder import Reminder
from typing import List

mock_reminders: List[Reminder] = [
    Reminder(
        gmail="testA@gmail.com",
        id=1,
        title="TestA",
        description="TestA",
        due_date="2022-01-01T00:00:00",
    ),
    Reminder(
        gmail="testB@gmail.com",
        id=1,
        title="TestB",
        description="TestB",
        due_date="2022-01-01T00:00:00",
    ),
    Reminder(
        gmail="testA@gmail.com",
        id=2,
        title="TestA",
        description="TestA",
        due_date="2022-01-01T00:00:00",
    ),
]


def main():
    injector: StorageInjector = PostgresInjectorImpl()  # Using default PostgresConfig
    storage_consumer: StorageConsumer = injector.build()
    # Insertion works fine
    for reminder in mock_reminders:
        storage_consumer.store_reminder(reminder)

    # Retrieval works fine
    current_reminders: List[Reminder] = storage_consumer.get_reminders("testA@gmail.com")
    for reminder in current_reminders:
        print(reminder.to_json())

    # Deletion works fine
    storage_consumer.delete_reminder("testB@gmail.com", 1)
    current_reminders: List[Reminder] = storage_consumer.get_reminders("testB@gmail.com")
    assert len(current_reminders) == 0

    # Update works fine
    storage_consumer.update_reminder(
        Reminder(
            gmail="testA@gmail.com",
            id=1,
            title="TestA",
            description="Wow, this is updated!",
            due_date="2022-01-01T00:00:00",
        ),
    )
    current_reminders: List[Reminder] = storage_consumer.get_reminders("testA@gmail.com")
    for reminder in current_reminders:
        print(reminder.to_json())

main()
