import http
import time
import uuid
from typing import Optional
import logging
import os

import aiohttp
from jose import jwt
from fastapi import HTTPException, Request, status as st
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(level=os.environ.get("LOG_LEVEL", "DEBUG"))


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, settings.ugc_secret, algorithms=[settings.algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid or expired token.')

        try:
            headers = {
                'Authorization': f'Bearer {credentials.credentials}',
                'X-Request-Id': str(uuid.uuid4())
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url='http://auth_service:8080/api/v1/auth/me') as status:
                    response = await status.json()
                    status_code = status.status
                    if status_code != st.HTTP_200_OK:
                        raise HTTPException(
                            status_code=status_code,
                            detail=response['detail'],
                        )
        except aiohttp.ServerTimeoutError as error:
            logger.info(credentials.credentials)
            raise HTTPException(status_code=st.HTTP_504_GATEWAY_TIMEOUT,
                                detail=str(error))
        except aiohttp.TooManyRedirects as error:
            raise HTTPException(status_code=st.HTTP_502_BAD_GATEWAY,
                                detail=str(error))
        except aiohttp.ClientError as error:
            raise HTTPException(status_code=st.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=str(error))

        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        return decode_token(jwt_token)


security_jwt = JWTBearer()
