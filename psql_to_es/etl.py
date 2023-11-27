import logging
import time
from datetime import datetime

import elasticsearch
import psycopg2
import redis

from etl.extractor.extractor import Extractor
from etl.loader.loader import EsLoader
from etl.transformer import Transformer
from utils.backoff import backoff
from utils.configs import BaseConfig
from utils.factory import EtlFactory, GenreEtlFactory, MovieEtlFactory, PersonEtlFactory
from utils.logger import get_logger
from utils.state import State
from utils.storage import RedisStorage


@backoff(elasticsearch.exceptions.ConnectionError)
@backoff(psycopg2.OperationalError)
def etl_process(
    logger: logging.Logger,
    extractor: Extractor,
    transformer: Transformer,
    state: State,
    loader: EsLoader,
) -> None:
    """Основной скрипт вызгурзки, преобразования и загрузки данных"""

    started = datetime.now()
    last_sync = state.get_state("updated")
    logger.info("Last sync %s", last_sync)
    last_update = last_sync or datetime.min

    for extracted in extractor.extract(last_update):
        transformed = transformer.transform(extracted)
        loader.load_data_to_index(transformed)
        state.set_state("updated", str(started))


def make_etl_factory(factory_name: str) -> EtlFactory:
    if factory_name == "movie":
        return MovieEtlFactory()
    elif factory_name == "genre":
        return GenreEtlFactory()
    elif factory_name == "person":
        return PersonEtlFactory()


def etl(etl_pipline_names: list[str]) -> None:
    for name in etl_pipline_names:
        factory = make_etl_factory(name)
        index = factory.create_index()
        state = State(RedisStorage(redis=redis_client, volume=index.redis_key))
        extractor = factory.create_extractor(
            postgres_dsn=configs.pg_dsn.dict(),
            batch_size=configs.batch_size,
            storage_state=state,
            logger=logger,
            index=index,
        )
        transformer = factory.create_transformer()
        loader = EsLoader(elastic_dsn=configs.es_dsn.host, logger=logger, index=index)
        etl_process(logger, extractor, transformer, state, loader)


if __name__ == "__main__":
    """Точка запуска процесса переноса данных в ElasticSearch"""

    configs = BaseConfig()
    logger = get_logger(__name__)
    redis_client = redis.from_url(url=configs.redis_dsn.host, decode_responses=True)

    etl_pipline_names = ["movie", "genre", "person"]

    while True:
        etl(etl_pipline_names)
        logger.info("Sleep %s", configs.sleep_time)
        time.sleep(configs.sleep_time)
