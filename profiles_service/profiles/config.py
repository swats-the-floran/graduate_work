from pydantic_settings import BaseSettings


class UGCConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8889

    class Config:
        env_prefix = 'ugc_'

    @property
    def url_review_rating(self):
        return f'http://{self.host}:{self.port}/api/v1/review_ratings?'

    @property
    def url_film_ratings(self):
        return f'http://{self.host}:{self.port}/api/v1/film_ratings?'


class BaseConfig(BaseSettings):
    ugc: UGCConfig = UGCConfig()


settings: BaseConfig = BaseConfig()
