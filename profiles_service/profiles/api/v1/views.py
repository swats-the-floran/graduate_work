import logging
from drf_spectacular.utils import extend_schema, extend_schema_view
from profiles.api.v1.mongo_requests import MongodbMixin

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from profiles.api.v1.permissions import IsAuthenticated
from profiles.api.v1.serializers import (
    BookmarkSerializer,
    FavoriteSerializer,
    FilmReviewSerializer,
    PersonDetailSerializer,
    PersonSerializer,
)
from profiles.models import (
    Bookmark,
    Favorite,
    FilmReview,
    Person,
)
from profiles.utils import StandardResultsSetPagination
from profiles.config import settings


RESULT_COUNT = 10


@extend_schema_view(
    list=extend_schema(summary='Get a persons\' list'),
    create=extend_schema(
        request=PersonSerializer,
        summary='Create a person',
    ),
    retrieve=extend_schema(summary='Get a person'),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(
        request=PersonSerializer,
        summary='Edit a person',
    ),
    destroy=extend_schema(summary='Delete a person'),
    detailed=extend_schema(
        summary='Get detailed person model with last reviews and its likes',
        responses=PersonDetailSerializer,
    ),
)
class PersonViewSet(viewsets.ModelViewSet, MongodbMixin):
    queryset = Person.objects.all().filter(is_active=True)
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)

    @action(detail=True, url_path='detailed')
    def detailed(self, request, pk=None):
        person = self.get_object()
        bookmarks = Bookmark.objects.filter(person=person).order_by('-created')[:RESULT_COUNT]
        favorites = Favorite.objects.filter(person=person).order_by('-created')[:RESULT_COUNT]
        reviews = FilmReview.objects.filter(person=person).order_by('-created')[:RESULT_COUNT]

        reviews_data = FilmReviewSerializer(reviews, many=True).data
        reviews_data = self._get_reviews_likes(reviews_data)

        favorites_data = FavoriteSerializer(favorites, many=True).data
        favorites_data = self._get_films_likes(favorites_data)

        serializer = PersonDetailSerializer(person, context={
            'request': request,
            'last_bookmarks': bookmarks,
            'last_favorites': favorites_data,
            'last_film_reviews': reviews_data,
        })

        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='Get user\'s bookmarks list'),
    create=extend_schema(
        request=BookmarkSerializer,
        summary='Create a bookmark',
    ),
    retrieve=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary='Delete user\'s bookmark'),
)
class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Bookmark.objects.filter(person=self.kwargs['person_pk'])


@extend_schema_view(
    list=extend_schema(summary='Get user\'s favorite movies list'),
    create=extend_schema(
        request=FavoriteSerializer,
        summary='Create user\'s favorite movie record',
    ),
    retrieve=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary='Delete user\'s favorite movie record'),
)
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(person=self.kwargs['person_pk'])


@extend_schema_view(
    list=extend_schema(summary='Get user\'s film reviews list'),
    create=extend_schema(
        request=FavoriteSerializer,
        summary='Create user\'s favorite movie record',
    ),
    retrieve=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(
        request=FilmReviewSerializer,
        summary='Edit user\'s film review',
    ),
    destroy=extend_schema(summary='Delete user\'s film review'),
    detail=extend_schema(
        responses=FilmReviewSerializer,
        summary='Detailed endpoint',
    ),
)
class FilmReviewViewSet(viewsets.ModelViewSet):
    serializer_class = FilmReviewSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return FilmReview.objects.filter(person=self.kwargs['person_pk'])
