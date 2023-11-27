from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_port: int = Field(env="ELASTIC_PORT", default="9200")
    es_host: str = Field(env="ELASTIC_HOST", default="0.0.0.0")
    redis_port: int = Field(env="REDIS_PORT", default="6379")
    redis_host: str = Field(env="REDIS_HOST", default="0.0.0.0")
    fast_api_port: int = Field(env="FAST_API_PORT", default="8888")
    fast_api_host: str = Field(env="FAST_API_HOST", default="0.0.0.0")

    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def elastic_dsn(self) -> str:
        return f"http://{self.es_host}:{self.es_port}"

    @property
    def fast_api_dsn(self) -> str:
        return f"http://{self.fast_api_host}:{self.fast_api_port}"


settings = TestSettings()
