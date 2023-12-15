from typing import OrderedDict
from drf_spectacular.utils import extend_schema, extend_schema_view
import requests

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
)
class PersonViewSet(viewsets.ModelViewSet):

    queryset = Person.objects.all().filter(is_active=True)
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    # permission_classes = (IsAuthenticated,)

    @staticmethod
    def _get_reviews_likes(reviews_data: OrderedDict) -> OrderedDict:
        review_ratings_endpoint = 'http://ugc_service:8889/api/v1/review_ratings?'
        params = ''
        for review in reviews_data:
            params += f'review_ids={review["id"]}&'
        url = review_ratings_endpoint + params

        try:
            resp = requests.get(url, timeout=2)
            review_scores = resp.json()
        except Exception:
            return reviews_data

        for review_score in review_scores:
            review_score['review_id']
            review_data = next(filter(lambda review: review['id'] == review_score['review_id'], reviews_data))  # find review for which we got likes
            review_data.update({'score': review_score['score']})
            review_data.update({'quantity': review_score['quantity']})

            print(review_data)

        print(reviews_data)

        return reviews_data


    @action(detail=True, url_path='detailed')
    def detailed(self, request, pk=None):
        person = self.get_object()
        bookmarks = Bookmark.objects.filter(person=person).order_by('-created')[:10]
        favorites = Favorite.objects.filter(person=person).order_by('-created')[:10]
        reviews = FilmReview.objects.filter(person=person).order_by('-created')[:10]

        reviews_data = FilmReviewSerializer(reviews, many=True).data
        reviews_data = self._get_reviews_likes(reviews_data)


        serializer = PersonDetailSerializer(person, context={
            'request': request,
            'last_bookmarks': bookmarks,
            'last_favorites': favorites,
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
    # permission_classes = (IsAuthenticated,)

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
    # permission_classes = (IsAuthenticated,)

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
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return FilmReview.objects.filter(person=self.kwargs['person_pk'])

    # @action(detail=True, url_path='detail', url_name='person-reviews-detail')
    # def detail(self):
    #     pass
