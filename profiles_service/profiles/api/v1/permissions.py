import re
import uuid

import jwt
import requests
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import BasePermission

from profiles.models import Person


class IsAuthenticated(BasePermission):

    @staticmethod
    def is_user_specific(request):
        path = request.get_full_path()
        person_pk = re.search('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', path)
        if person_pk is None:
            return ''
        return person_pk

    @staticmethod
    def correct_token(request) -> str:
        auth = get_authorization_header(request).split()
        if not auth or auth[0].decode().lower() != 'bearer' or len(auth) != 2:
            return ''

        try:
            token = auth[1].decode()
        except UnicodeError:
            return ''

        return token

    @staticmethod
    def token_expired(token: str) -> bool:
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Request-Id': str(uuid.uuid4()),
        }
        resp = requests.get('http://auth_service:8080/api/v1/auth/me', headers=headers)

        return resp.ok

    @staticmethod
    def token_belongs_user(token, person_pk):
        token_email = jwt.decode(token, key='secret', algorithms=['HS256'])['email']
        person_obj = Person.objects.filter(pk=person_pk).first()
        if person_obj and person_obj.email == token_email:
            return False

    def has_permission(self, request, view):
        person_pk = self.is_user_specific(request)
        if not person_pk:
            return True

        token = self.correct_token(request)
        if not token:
            return False

        if self.token_expired(token):
            return False

        if self.token_belongs_user(token, person_pk):
            return True

        return False

