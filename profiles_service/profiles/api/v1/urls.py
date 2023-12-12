from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from .views import (
    BookmarkAPIView,
    PersonAPIView,
    DeactivatePersonAPIView,
    FavoriteAPIView,
    BookmarksListView,
    FavoritesListView,
    PersonViewSet
)


router = SimpleRouter()
router.register('users', PersonViewSet)


urlpatterns = router.urls
urlpatterns += [
    # profiles
    # path('users/', PersonAPIView.as_view(), name='create_user'),
    # path('users/whoami/', PersonAPIView.as_view(), name='get_user_info'),
    # path('users/<uuid:uuid>/', PersonAPIView.as_view(), name='update_user'),
    # path('users/<uuid:uuid>/deactivate/', DeactivatePersonAPIView.as_view(), name='deactivate_user'),
    # path('users/<uuid:uuid>/detail/', PersonAPIView.as_view(), name='get_detailed_user_info'),
    # bookamarks
    # path('users/<uuid:uuid>/bookmarks/', BookmarkAPIView.as_view(), name='bookmarks'),
    # path('users/<uuid:uuid>/bookmarks/list', BookmarksListView.as_view(), name='bookmarks_list'),
    # favorites
    # path('users/favorite_movies/', FavoriteAPIView.as_view(), name='favorite_movie_create'),
    # path('users/favorite_movies/<int:favorite_movie_id>/', FavoriteAPIView.as_view(), name='favorite_movie_delete'),
    # path('users/<uuid:uuid>/favorites/list/', FavoritesListView.as_view(), name='favorites_list'),
    # reviews
    # openapi
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('openapi-profiles/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
