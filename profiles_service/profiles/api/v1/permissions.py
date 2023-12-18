import re
import uuid

import jwt
import requests
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import BasePermission

from profiles.models import Person


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # TODO: exceptions with messages

        #if endpoint does not require user id, there is no need for permission
        path = request.get_full_path()
        person_pk = re.search('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', path)
        if person_pk is None:
            return True

        # in other case we check credentials correcttness
        auth = get_authorization_header(request).split()
        if not auth or auth[0].decode().lower() != 'bearer' or len(auth) != 2:
            return False

        try:
            token = auth[1].decode()
        except UnicodeError:
            return False

        headers = {
            'Authorization': f'Bearer {token}',
            'X-Request-Id': str(uuid.uuid4()),
        }
        resp = requests.get('http://auth_service:8080/api/v1/auth/me', headers=headers)

        if not resp.ok:
            return False

        # check if token belongs to the user
        token_email = jwt.decode(token, key='secret', algorithms=['HS256'])['email']
        person_obj = Person.objects.filter(pk=person_pk).first()
        if person_obj and person_obj.email == token_email:
            return False

        return False

