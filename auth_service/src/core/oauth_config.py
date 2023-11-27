from authlib.integrations.starlette_client import OAuth
from pydantic_settings import BaseSettings
from models.entities import SocialNetwork


class YandexSocialAuth(BaseSettings):
    name: str = SocialNetwork.yandex
    authorize_url: str = 'https://oauth.yandex.ru/authorize'
    access_token_url: str = 'https://oauth.yandex.ru/token'
    api_base_url: str = 'https://login.yandex.ru/info'
    client_id: str = ...
    client_secret: str = ...

    class Config:
        env_prefix = 'yandex_'


class GoogleSocialAuth(BaseSettings):
    name: str = SocialNetwork.google
    client_id: str = ...
    client_secret: str = ...

    class Config:
        env_prefix = 'google_'


oauth = OAuth()
oauth.register(**dict(YandexSocialAuth()))
oauth.register(**dict(GoogleSocialAuth()))