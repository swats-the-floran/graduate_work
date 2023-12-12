from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets

from profiles.models import Person, Bookmark, Favorite
from profiles.api.v1.serializers import BookmarkSerializer, FavoriteSerializer, PersonSerializer
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

