import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ugc_project_name: str = "movies_ugc"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ugc_fast_api_host: str = "0.0.0.0"
    ugc_fast_api_port: int = 8889

    auth_host: str = "0.0.0.0"
    auth_port: int = 8080

    ugc_secret: str = "secret"
    algorithm: str = "HS256"

    # kafka_host: str = "broker"
    # kafka_port: str = "29092"

    mongo_host: str = "mongos1"
    mongo_port: int = 27017

    sentry_dsn: str = "https://e24a3aedb026bfac6a3aa05ca67e919a@o4506173799727104.ingest.sentry.io/4506173902618624"

    model_config = SettingsConfigDict(env_file=".env")


settings: BaseConfig = BaseConfig()
