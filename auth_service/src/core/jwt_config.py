from datetime import timedelta

from pydantic import BaseModel, Field


class Settings(BaseModel):
    authjwt_secret_key: str = Field(env="SECRET", default="secret")
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_token_location: set = {"headers"}
    access_expires: int = timedelta(minutes=2)
    refresh_expires: int = timedelta(days=30)


setting_jwt = Settings()
