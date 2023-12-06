from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from profiles.models import Person
from profiles.api.v1.serializers import PersonResponseSerializer
from profiles.services.profile_service import PersonService


class PersonAPIView(APIView):

    @staticmethod
    def _get_person(uuid):
        return get_object_or_404(Person, id=uuid)

    def get(self, request, uuid=None):
        if uuid:
            user = self._get_person(uuid)
            if not user.is_active:
                return Response({"detail": "user is not active"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PersonResponseSerializer(user)
        else:
            users = Person.objects.filter(is_active=True).all()
            serializer = PersonResponseSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = PersonService.create_user(request.data)

        if not user.is_active:
            return Response({"detail": "user is not active"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, uuid=None):
        if not uuid:
            return Response({'detail': 'Missing UUID'}, status=status.HTTP_400_BAD_REQUEST)

        user = self._get_person(uuid)

        if not user.is_active:
            return Response({"detail": "user is not active"}, status=status.HTTP_404_NOT_FOUND)

        updated_user = PersonService.update_user(user, request.data)
        serializer = PersonResponseSerializer(updated_user)
        return Response(serializer.data)


class DeactivatePersonAPIView(APIView):

    def delete(self, request, uuid=None):
        if not uuid:
            return Response({'detail': 'Missing UUID'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(Person, id=uuid)

        if request.data.get('completely'):
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

