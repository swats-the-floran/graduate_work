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


class DBProfile(BaseSettings):
    db: str = "profiles"
    user: str = "postgres"
    password: str = "password"
    host: str = "0.0.0.0"
    port: int = 5432

    class Config:
        env_prefix = 'profile_pg_'

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class BaseConfig(BaseSettings):
    db: DBConfig = DBConfig()
    db_profile: DBProfile = DBProfile()


settings: BaseConfig = BaseConfig()
