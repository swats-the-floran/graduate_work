from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from profiles.models import Person, Bookmark, Favorite
from profiles.api.v1.serializers import PersonResponseSerializer, FavoriteSerializer, BookmarkSerializer
from profiles.profile_service import PersonService
from profiles.utils import StandardResultsSetPagination


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

    # def delete(self, request, uuid=None):
    #     if not uuid:
    #         return Response({'detail': 'Missing UUID'}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     user = get_object_or_404(Person, id=uuid)
    #     if request.data.get('completely'):
    #         user.delete_completely()
    #     elif not user.is_active:
    #         return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         user.delete()
    #
    #     return Response(status=status.HTTP_204_NO_CONTENT)


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


class BookmarksListView(generics.ListAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        person_id = self.kwargs.get("uuid")
        return Bookmark.objects.filter(person_id=person_id).all()


class FavoritesListView(generics.ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        person_id = self.kwargs.get("uuid")
        return Favorite.objects.filter(person_id=person_id).all()


class BookmarkAPIView(APIView):
    serializer_class = BookmarkSerializer


class FavoriteAPIView(APIView):
    serializer_class = FavoriteSerializer

    def post(self, request):
        favorite_movie = PersonService.create_favorite_movie(request.data)
        serializer = FavoriteSerializer(favorite_movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, favorite_movie_id=None):
        if not favorite_movie_id:
            return Response({'detail': 'Missing ID'}, status=status.HTTP_400_BAD_REQUEST)

        favorite_movie = get_object_or_404(Favorite, id=favorite_movie_id)

        favorite_movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

