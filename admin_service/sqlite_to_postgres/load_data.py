from context_managers import PostgreSQLContextManager, SQLiteContextManager
from helpers import dict_factory
from psycopg2.extras import DictCursor
from repositories import PostgresRepository, SQLiteRepository
from services import SQLiteToPsqlService
from settings import DSN_PSQL, SQLITE_DB_PATH, logger

if __name__ == "__main__":
    with SQLiteContextManager(SQLITE_DB_PATH, dict_factory) as sqlite_con:
        with PostgreSQLContextManager(DSN_PSQL, DictCursor) as postgres_con:
            service = SQLiteToPsqlService(
                sqlite_repo=SQLiteRepository(sqlite_con),
                psql_repo=PostgresRepository(postgres_con),
            )
            logger.info("Начинаю перенос данных из sqlite в postgres.")
            service.transfer_data_sqlite_to_psql()
            logger.info("Данные успешно перенесены.")
