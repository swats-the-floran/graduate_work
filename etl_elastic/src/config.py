from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    db: str = "cinema"
    user: str = "postgres"
    password: str = "password"
    host: str = "0.0.0.0"
    port: int = 5432

    class Config:
        env_prefix = 'postgres_'

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ESConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 9200

    class Config:
        env_prefix = 'elastic_'

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class BaseConfig(BaseSettings):
    db: DBConfig = DBConfig()
    es: ESConfig = ESConfig()


settings: BaseConfig = BaseConfig()
