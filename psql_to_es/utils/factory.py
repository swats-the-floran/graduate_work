import abc
import logging

from etl.extractor.extractor import Extractor, GenreExtractor, MovieExtractor, PersonExtractor
from etl.loader.index import GenreIndex, Index, MovieIndex, PersonIndex
from etl.transformer import GenreTransformer, MovieTransformer, PersonTransformer, Transformer

from .configs import PgSettings
from .state import State


class EtlFactory(abc.ABC):
    @abc.abstractmethod
    def create_extractor(
        self, postgres_dsn: PgSettings, batch_size: int, storage_state: State, logger: logging.Logger, index: Index
    ) -> Extractor:
        """return Extractor"""

    @abc.abstractmethod
    def create_transformer(self) -> Transformer:
        """return Transformer"""

    @abc.abstractmethod
    def create_index(self) -> Index:
        """return Index"""


class MovieEtlFactory(EtlFactory):
    def create_extractor(
        self, postgres_dsn: PgSettings, batch_size: int, storage_state: State, logger: logging.Logger, index: Index
    ) -> MovieExtractor:
        return MovieExtractor(postgres_dsn, batch_size, storage_state, logger, index)

    def create_transformer(self) -> MovieTransformer:
        return MovieTransformer()

    def create_index(self) -> MovieIndex:
        return MovieIndex()


class GenreEtlFactory(EtlFactory):
    def create_extractor(
        self, postgres_dsn: PgSettings, batch_size: int, storage_state: State, logger: logging.Logger, index: Index
    ) -> GenreExtractor:
        return GenreExtractor(postgres_dsn, batch_size, storage_state, logger, index)

    def create_transformer(self) -> GenreTransformer:
        return GenreTransformer()

    def create_index(self) -> GenreIndex:
        return GenreIndex()


class PersonEtlFactory(EtlFactory):
    def create_extractor(
        self, postgres_dsn: PgSettings, batch_size: int, storage_state: State, logger: logging.Logger, index: Index
    ) -> PersonExtractor:
        return PersonExtractor(postgres_dsn, batch_size, storage_state, logger, index)

    def create_transformer(self) -> PersonTransformer:
        return PersonTransformer()

    def create_index(self) -> PersonIndex:
        return PersonIndex()
