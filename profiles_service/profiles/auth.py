import http
import logging
import uuid

import requests
from requests.exceptions import Timeout, TooManyRedirects, RequestException
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {"email": username, "password": password}
        headers = {'X-Request-Id': str(uuid.uuid4())}
        try:
            response = requests.post(url, headers=headers, params=payload)
        except (TooManyRedirects, RequestException, Timeout):
            logging.error('auth_server error')
            return None
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        user_data = data.get("user")

        try:
            user, created = User.objects.get_or_create(id=user_data['id'],)
            user.email = user_data.get('email')
            user.first_name = user_data.get('first_name')
            user.last_name = user_data.get('second_name')

            user.is_admin = False
            for role in user_data.get('roles'):
                if role.get('name') == "admin":
                    user.is_admin = True
                    break
            user.is_active = user_data.get('is_active')
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
