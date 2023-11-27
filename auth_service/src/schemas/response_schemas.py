from typing import Any

from pydantic import BaseModel


class FastAPIResponse(BaseModel):
    pass


class FastAPIErrorResponse(FastAPIResponse):
    detail: str


class FastAPISuccessResponse(FastAPIResponse):
    result: Any
