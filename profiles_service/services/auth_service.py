import time
import os

from django.http import JsonResponse
from rest_framework import status

from jose import jwt
from jose.exceptions import JWTError


def decode_token(token: str, secret_key: str, algorithms: list) -> dict | None:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=algorithms)

        if decoded_token['exp'] < time.time():
            raise JWTError("Token has expired")

        return decoded_token
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None


def jwt_required(get_response):
    def middleware(request):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        if not authorization_header or not authorization_header.startswith('Bearer '):
            return JsonResponse(
                {'detail': 'Authentication credentials were not provided or invalid.'},
                status=status.HTTP_403_FORBIDDEN
            )

        jwt_token = authorization_header.split(' ')[1]
        decoded_token = decode_token(
            token=jwt_token,
            algorithms=[os.environ.get("ALGORITHM")],
            secret_key=os.environ.get("SECRET_KEY"),
        )
        if not decoded_token:
            return JsonResponse({'detail': 'Invalid or expired token'}, status=status.HTTP_403_FORBIDDEN)

        request.user = decoded_token
        return get_response(request)

    return middleware
