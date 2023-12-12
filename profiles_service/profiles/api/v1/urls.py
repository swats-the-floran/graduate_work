from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

from .views import (
    PersonViewSet,
    BookmarkViewSet,
    FavoriteViewSet,
)


router = SimpleRouter()
router.register('persons', PersonViewSet)

persons_router = NestedSimpleRouter(router, r'persons', lookup='person')
persons_router.register(r'bookmarks', BookmarkViewSet, basename='user-bookmarks')
persons_router.register(r'favorites', FavoriteViewSet, basename='user-favorites')


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(persons_router.urls)),
    # openapi
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('openapi-profiles/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
