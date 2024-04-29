import time
from typing import Tuple
import psycopg2
import threading

from services.reminder_service import MovementService
from models.configuration import Configuration


# Call PostgresDbMovementService.run() to start the service
# in a separate thread
class PostgresMovementService(MovementService):
    def __init__(
        self,
        flag: threading.Event,
        config: Configuration,
    ) -> None:
        super().__init__()
        self.__sleep_duration = config.app_config.waiting_time
        self.__flag = flag
        self.__remind_before = config.app_config.remind_before
        self.__conn = psycopg2.connect(**config.db_config.to_dict())

    def move_pending_reminder(self) -> bool:
        try:
            query_str: str = """
                SELECT id, chat_id, title, description, due_date
                FROM reminders
                WHERE due_date <= NOW() + INTERVAL '%s seconds'
                FOR UPDATE
                SKIP LOCKED
                LIMIT 1
            """
            # Start transaction
            cursor = self.__conn.cursor()
            cursor.execute(query_str, (self.__remind_before,))
            reminder: Tuple = cursor.fetchone()
            if not reminder:
                # Commit transaction
                self.__conn.commit()
                return False
            # For each reminder, move it to the reminder_delivery table
            # and delete it from the reminders table
            query_str = """
                    INSERT INTO reminder_delivery (id, chat_id, title, description, due_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
            cursor.execute(
                query_str,
                (
                    reminder[0],
                    reminder[1],
                    reminder[2],
                    reminder[3],
                    reminder[4],
                ),
            )
            query_str = """
                DELETE FROM reminders
                WHERE id = %s AND chat_id = %s
            """
            cursor.execute(query_str, (reminder[0], reminder[1]))
            # Commit transaction
            self.__conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
            return False

    def run(self) -> None:
        while not self.__flag.is_set():
            # If there is a reminder to move, move it and continue to query
            # the database
            if self.move_pending_reminder():
                continue
            # else, sleep for a while
            time.sleep(self.__sleep_duration)
