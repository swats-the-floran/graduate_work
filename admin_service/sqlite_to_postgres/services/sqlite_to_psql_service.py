from typing import Type

from errors import BaseDBException
from models import BaseModel, FilmworkModel, GenreFilmworkModel, GenreModel, PersonFilmworkModel, PersonModel
from repositories import PostgresRepository, SQLiteRepository
from settings import logger


class SQLiteToPsqlService:
    BATCH_SIZE = 100

    TUPLE_TYPE_MODELS: Type[BaseModel] = (
        FilmworkModel,
        PersonModel,
        GenreModel,
        GenreFilmworkModel,
        PersonFilmworkModel,
    )

    def __init__(self, sqlite_repo: SQLiteRepository, psql_repo: PostgresRepository) -> None:
        self._sqlite_repo: SQLiteRepository = sqlite_repo
        self._psql_repo: PostgresRepository = psql_repo

    def is_equal_count_row_in_databases(self) -> bool:
        is_equals = []
        for model in self.TUPLE_TYPE_MODELS:
            is_equals.append(self._sqlite_repo.get_count(model) == self._psql_repo.get_count(model))

        return all(is_equals)

    def is_equal_rows_in_databases(self) -> bool:
        is_equals = []
        for model in self.TUPLE_TYPE_MODELS:
            is_equals.append(
                self._sqlite_repo.get_all(model, order_by="id") == self._psql_repo.get_all(model, order_by="id")
            )
        return all(is_equals)

    def transfer_data_sqlite_to_psql(self) -> None:
        try:
            for model in self.TUPLE_TYPE_MODELS:
                self._save(model)
            self._psql_repo.commit()
        except BaseDBException as exc:
            logger.error(exc)

    def _save(self, model: BaseModel) -> None:
        for models_batch in self._sqlite_repo.get_all_from_model_batch(model, self.BATCH_SIZE):
            self._psql_repo.save_all(model, models=models_batch)
