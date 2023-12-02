from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from profiles.models import Person
from profiles.api.v1.serializers import PersonResponseSerializer
from profiles.profile_service import PersonService


class PersonAPIView(APIView):
    def get(self, request, uuid=None):
        if uuid:
            try:
                user = Person.objects.get(id=uuid)
                serializer = PersonResponseSerializer(user)
                return Response(serializer.data)
            except Person.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = Person.objects.all()
            serializer = PersonResponseSerializer(users, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = PersonService.create_user(request.data)
        serializer = PersonResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, uuid=None):
        if not uuid:
            return Response({'detail': 'Missing UUID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Person.objects.get(id=uuid)
        except Person.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        updated_user = PersonService.update_user(user, request.data)
        serializer = PersonResponseSerializer(updated_user)
        return Response(serializer.data)


class DeactivatePersonAPIView(APIView):

    def patch(self, request, uuid=None):
        if not uuid:
            return Response({'detail': 'Missing UUID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Person.objects.get(id=uuid)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Person.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
