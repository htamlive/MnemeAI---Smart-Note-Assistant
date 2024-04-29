import random
import threading

from services.reminder_service import (
    ReminderDeliveryFactory,
    ReminderPersistentService,
    ReminderDeliveryService,
    MovementService,
)
from postgres.delivery_service import PostgresDeliveryService
from postgres.movement_service import PostgresMovementService
from postgres.storage_service import PostgresStorageService
from models.configuration import Configuration


class MockApiClient:
    def send_reminder(
        self,
        id: str,
        chat_id: str,
        title: str,
        description: str,
        due_date: str,
    ) -> dict:
        if random.random() < 0.5:
            return {
                "status_code": 500,
                "message": "Internal server error. Please try again later.",
            }
        return {
            "status_code": 200,
            "message": f"Reminder {id} with {title} {description} {due_date} has been sent to {chat_id}",
        }


class PostgresServiceFactory(ReminderDeliveryFactory):
    def __init__(
        self,
        flag: threading.Event,
        config: Configuration = Configuration.default(),
        api_client=MockApiClient(),
    ) -> None:
        self.__config = config
        self.__flag = flag
        self.__api_client = api_client

    def storage_service(self) -> ReminderPersistentService:
        return PostgresStorageService(self.__config)

    def movement_service(self) -> MovementService:
        return PostgresMovementService(config=self.__config, flag=self.__flag)

    def delivery_service(self) -> ReminderDeliveryService:
        return PostgresDeliveryService(
            config=self.__config, flag=self.__flag, api_client=self.__api_client
        )
