from datetime import datetime
import psycopg2

from typing import List

import psycopg2.errors
from reminder import Reminder
from persistent_service import ReminderPersistentService


class PostgresConfig:
    def __init__(
        self, username: str, password: str, host: str, port: int, dbname: str
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname

    def connection_str(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    @staticmethod
    def from_env() -> "PostgresConfig":
        return PostgresConfig(
            username="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            dbname="note_persistence",
        )


class PostgresDbService(ReminderPersistentService):
    def __init__(self, config: PostgresConfig) -> None:
        self.__conn = psycopg2.connect(
            user=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            dbname=config.dbname,
        )

    def close(self):
        self.__conn.close()

    def store_reminder(self, reminder: Reminder):
        try:
            query_str: str = """
            INSERT INTO reminders (id, gmail, title, description, due_date)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor = self.__conn.cursor()
            cursor.execute(
                query_str,
                (
                    reminder.id,
                    reminder.gmail,
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

    def get_reminders(self, gmail: str) -> List[Reminder]:
        try:
            query_str: str = """
            SELECT * FROM reminders WHERE gmail = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(query_str, (gmail,))
            reminders = [
                Reminder(
                    gmail=row[1],
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

    def delete_reminder(self, gmail: str, id: str):
        try:
            query_str: str = """
            DELETE FROM reminders WHERE gmail = %s AND id = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(query_str, (gmail, id))
            cursor.close()
            self.__conn.commit()
        except Exception as e:
            print(e)
            self.__conn.rollback()

    def update_reminder(self, reminder: Reminder):
        try:
            query_str: str = """
            UPDATE reminders SET title = %s, description = %s, due_date = %s, updated_at = CURRENT_TIMESTAMP
            WHERE gmail = %s AND id = %s
            """
            cursor = self.__conn.cursor()
            cursor.execute(
                query_str,
                (
                    reminder.title,
                    reminder.description,
                    reminder.due_date,
                    reminder.gmail,
                    reminder.id,
                ),
            )
            cursor.close()
            self.__conn.commit()
        except Exception as e:
            print(e)
            self.__conn.rollback()
