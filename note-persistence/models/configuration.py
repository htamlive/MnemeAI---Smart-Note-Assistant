import os


class DatabaseConfiguration:
    def __init__(
        self, username: str, password: str, host: str, port: int, dbname: str
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname

    @property
    def connection_str(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    def to_dict(self) -> dict:
        return {
            "user": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
        }

    @staticmethod
    def default() -> "DatabaseConfiguration":
        return DatabaseConfiguration(
            username="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            dbname="note_persistence",
        )

    @staticmethod
    def from_env() -> "DatabaseConfiguration":
        # Check if environment variables are set
        if not all(
            [
                os.getenv("DB_USERNAME"),
                os.getenv("DB_PASSWORD"),
                os.getenv("DB_HOST"),
                os.getenv("DB_PORT"),
                os.getenv("DB_NAME"),
            ]
        ):
            print("Environment variables not set")
            return DatabaseConfiguration.default()
        return DatabaseConfiguration(
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            dbname=os.getenv("DB_NAME"),
        )


class ApplicationConfiguration:
    def __init__(
        self,
        workers_per_service: int,
        waiting_time: int,
        remind_before: int,
        retry_limit: int,
    ) -> None:
        self.workers_per_service = workers_per_service
        self.waiting_time = waiting_time  # in seconds
        self.remind_before = remind_before  # in seconds
        self.retry_limit = retry_limit

    @staticmethod
    def default() -> "ApplicationConfiguration":
        return ApplicationConfiguration(
            workers_per_service=5, waiting_time=5, remind_before=10 * 60, retry_limit=5
        )

    @staticmethod
    def from_env() -> "ApplicationConfiguration":
        if not all(
            [
                os.getenv("MAX_WORKERS"),
                os.getenv("WAITING_TIME"),
                os.getenv("REMIND_BEFORE"),
                os.getenv("RETRY_LIMIT"),
            ]
        ):
            print("Environment variables not set")
            return ApplicationConfiguration.default()
        return ApplicationConfiguration(
            workers_per_service=int(os.getenv("MAX_WORKERS")),
            waiting_time=int(os.getenv("WAITING_TIME")),
            remind_before=int(os.getenv("REMIND_BEFORE")),
            retry_limit=int(os.getenv("RETRY_LIMIT")),
        )


class Configuration:
    def __init__(
        self, db_config: DatabaseConfiguration, app_config: ApplicationConfiguration
    ) -> None:
        self.db_config = db_config
        self.app_config = app_config

    @staticmethod
    def default() -> "Configuration":
        return Configuration(
            db_config=DatabaseConfiguration.default(),
            app_config=ApplicationConfiguration.default(),
        )
