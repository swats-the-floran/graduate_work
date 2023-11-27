from typing import Optional

from pydantic import BaseModel


class UserData(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: str
    user_id: Optional[str]
    phone_number: Optional[str]


class DataModel(BaseModel):
    template: str
    subject: str
    user_list: list
