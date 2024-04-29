import psycopg2

from typing import List

import psycopg2.errors
from models.reminder import Reminder
from models.configuration import Configuration
from services.reminder_service import ReminderPersistentService

class PostgresStorageService(ReminderPersistentService):
    def __init__(self, config: Configuration) -> None:
        self.__conn = psycopg2.connect(**config.db_config.to_dict())

    def close(self):
        self.__conn.close()

    def store_reminder(self, reminder: Reminder):
        try:
            query_str: str = """
            INSERT INTO reminders (id, chat_id, title, description, due_date)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor = self.__conn.cursor()
            cursor.execute(
                query_str,
                (
                    reminder.id,
                    reminder.chat_id,
                    reminder.title,
                    reminder.description,
                    reminder.due_date,
                ),
            )
            self.__conn.commit()
        except (Exception, psycopg2.Error) as error:
            # Rolling back the transaction in case of error
            self.__conn.rollback()
            print(f"Error: {error}")
        finally:
            if self.__conn:
                cursor.close()

    def get_reminders(self, chat_id: str) -> List[Reminder]:
        try:
            query_str: str = """
            SELECT chat_id, id, title, description, due_date
            FROM reminders
            WHERE chat_id = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(query_str, (chat_id,))
            reminders = [
                Reminder(
                    chat_id=row[1],
                    id=row[0],
                    title=row[2],
                    description=row[3],
                    due_date=row[4],
                )
                for row in cursor.fetchall()
            ]
            cursor.close()
            return reminders
        except Exception as e:
            print(e)
            return []

    def delete_reminder(self, chat_id: str, id: str):
        try:
            query_str: str = """
            DELETE FROM reminders
            WHERE chat_id = %s AND id = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(query_str, (chat_id, id))
            cursor.close()
            self.__conn.commit()
        except Exception as e:
            print(e)
            self.__conn.rollback()

    def update_reminder(self, reminder: Reminder):
        try:
            query_str: str = """
            UPDATE reminders
            SET title = %s, description = %s, due_date = %s, updated_at = CURRENT_TIMESTAMP
            WHERE chat_id = %s AND id = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(
                query_str,
                (
                    reminder.title,
                    reminder.description,
                    reminder.due_date,
                    reminder.chat_id,
                    reminder.id,
                ),
            )
            cursor.close()
            self.__conn.commit()
        except Exception as e:
            print(e)
            self.__conn.rollback()
