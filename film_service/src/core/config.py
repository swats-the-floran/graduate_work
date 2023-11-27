import os

from pydantic import BaseSettings, Field


class RedisConfig(BaseSettings):
    host: str = Field(env="REDIS_HOST", default="0.0.0.0")
    port: int = Field(env="REDIS_PORT", default=6379)
    cache_expire: int | float = Field(env="CACHE_EXPIRE", default=300)


class ElasticConfig(BaseSettings):
    host: str = Field(env="ELASTIC_HOST", default="0.0.0.0")
    port: int = Field(env="ELASTIC_PORT", default=9200)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/"


class BaseConfig(BaseSettings):
    project_name: str = Field(env="PROJECT_NAME", default="movies")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    host: str = Field(env="FAST_API_HOST", default="0.0.0.0")
    port: int = Field(env="FAST_API_PORT", default=8888)

    host_auth: str = Field(env="AUTH_HOST", default="0.0.0.0")
    port_auth: int = Field(env="AUTH_PORT", default=8080)

    jwt_secret_key: str = Field(env="SECRET", default="secret")
    jwt_algorithm: str = Field(env="ALGORITHM", default="secret")

    sentry_dsn: str = Field(env="SENTRY_DSN", default="https://e24a3aedb026bfac6a3aa05ca67e919a@o4506173799727104.ingest.sentry.io/4506173902618624")

    redis: RedisConfig = RedisConfig()
    elastic: ElasticConfig = ElasticConfig()


settings: BaseConfig = BaseConfig()
