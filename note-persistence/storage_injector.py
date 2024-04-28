from storage_consumer import StorageConsumer
from postgres_service import PostgresConfig, PostgresDbService

class StorageInjector:
    def build(self) -> StorageConsumer:
        pass

class PostgresInjectorImpl(StorageInjector):
    def __init__(self, config: PostgresConfig = PostgresConfig.from_env()) -> None:
        super().__init__()
        self.__config = config

    def build(self) -> StorageConsumer:
        return StorageConsumer(PostgresDbService(self.__config))
