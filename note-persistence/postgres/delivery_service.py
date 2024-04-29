from datetime import datetime
import threading
import time
import psycopg2

from services.reminder_service import ReminderDeliveryService
from models.configuration import Configuration

class PostgresDeliveryService(ReminderDeliveryService):
    def __init__(
        self,
        config: Configuration,
        flag: threading.Event,
        api_client,
    ) -> None:
        super().__init__()
        self._waiting_time = config.app_config.waiting_time
        self._retry_limit = config.app_config.retry_limit
        self._conn = psycopg2.connect(**config.db_config.to_dict())
        self._flag = flag
        self._api_client = (
            api_client  # This is the API client that will be used to send the reminders
        )

    def deliver_reminder(self) -> bool:
        try:
            query_str: str = """
                SELECT chat_id, id, title, description, due_date, n_retries
                FROM reminder_delivery
                WHERE last_retry IS NULL OR last_retry < NOW() - INTERVAL '%s seconds'
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            """
            # start transaction
            cursor = self._conn.cursor()
            cursor.execute(query_str, (self._waiting_time,))
            reminder = cursor.fetchone()
            if not reminder:
                # commit transaction
                self._conn.commit()
                return False
            # For each reminder, call the delivery service and wait for the response
            # If the response is successful, delete the reminder from the reminder_delivery table
            # If the response is not successful, update the reminder with the new retry count
            # or log the reminder for manual intervention and delete the reminder if the retry limit is reached
            response = self._api_client.send_reminder(
                chat_id=reminder[0],
                id=reminder[1],
                title=reminder[2],
                description=reminder[3],
                due_date=reminder[4],
            )
            query_str: str = ""
            dropped = False
            if response["status_code"] == 200:
                query_str = """
                    DELETE FROM reminder_delivery
                    WHERE id = %s AND chat_id = %s
                """
            else:
                if reminder[5] >= self._retry_limit:
                    query_str = """
                        DELETE FROM reminder_delivery
                        WHERE id = %s AND chat_id = %s
                    """
                    dropped = True
                else:
                    query_str = """
                    UPDATE reminder_delivery
                    SET n_retries = n_retries + 1, last_retry = NOW()
                    WHERE id = %s AND chat_id = %s
                    """
            cursor.execute(query_str, (reminder[1], reminder[0]))
            # commit transaction
            self._conn.commit()
            print(response["message"])
            if dropped:
                print(
                    f"Reminder with id {reminder[1]} and chat_id {reminder[0]} \
                            \nTitle: {reminder[2]} \
                                \nDescription: {reminder[3]} \
                                    \nDue Date: {reminder[4]} \
                                        \nFailed to deliver after {self._retry_limit} retries. Dropped at {datetime.now().isoformat()}."
                )
            return True
        except psycopg2.Error as error:
            self._conn.rollback()
            print(f"Error: {error}")
        except Exception as e:
            self._conn.rollback()
            print(f"Error: {e}")

    def run(self) -> None:
        while not self._flag.is_set():
            if self.deliver_reminder():
                continue
            time.sleep(self._waiting_time)
