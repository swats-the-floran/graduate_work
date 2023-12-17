import re
import uuid
from drf_spectacular.utils import extend_schema, extend_schema_view
from typing import OrderedDict

import requests
import jwt
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # TODO: exceptions with messages

        # if endpoint does not require user id, there is no need for permission
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
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().filter(is_active=True)
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _get_reviews_likes(reviews_data: OrderedDict) -> OrderedDict:

        params = ''
        for review in reviews_data:
            params += f'review_ids={review["id"]}&'
        url = settings.url + params

        try:
            resp = requests.get(url, timeout=2)
            review_scores = resp.json()
        except Exception:
            return reviews_data

        if not resp.ok:
            return reviews_data

        for review_score in review_scores:
            review_data = next(filter(lambda review: review['id'] == review_score['review_id'],
                                      reviews_data))  # find review for which we got likes
            review_data.update({'score': review_score['score']})
            review_data.update({'quantity': review_score['quantity']})

        return reviews_data

    @staticmethod
    def _get_films_likes(films_data: OrderedDict) -> OrderedDict:
        film_ratings_endpoint = 'http://ugc_service:8889/api/v1/film_ratings?'
        params = ''
        for film in films_data:
            params += f'film_ids={film["film"]["id"]}&'
        url = film_ratings_endpoint + params

        try:
            resp = requests.get(url, timeout=2)
            film_scores = resp.json()
        except Exception:
            return films_data

        if not resp.ok:
            return films_data

        for film_score in film_scores:
            film_data = next(filter(lambda film: film['film']['id'] == film_score['movie_id'], films_data))
            film_data['film'].update({'score': film_score['score']})
            film_data['film'].update({'quantity': film_score['quantity']})

        return films_data

    @action(detail=True, url_path='detailed')
    def detailed(self, request, pk=None):
        person = self.get_object()
        bookmarks = Bookmark.objects.filter(person=person).order_by('-created')[:10]
        favorites = Favorite.objects.filter(person=person).order_by('-created')[:10]
        reviews = FilmReview.objects.filter(person=person).order_by('-created')[:10]

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
