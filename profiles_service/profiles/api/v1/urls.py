from django.urls import path
from .views import BookmarkAPIView, PersonAPIView, DeactivatePersonAPIView, FavoriteAPIView


urlpatterns = [
    # profiles
    path('users/', PersonAPIView.as_view(), name='create_user'),
    path('users/whoami/', PersonAPIView.as_view(), name='get_user_info'),
    path('users/<uuid:uuid>/', PersonAPIView.as_view(), name='update_user'),
    path('users/<uuid:uuid>/deactivate/', DeactivatePersonAPIView.as_view(), name='deactivate_user'),
    # path('users/<uuid:uuid>/detail/', PersonAPIView.as_view(), name='get_detailed_user_info'),

    # bookamarks
    path('users/<uuid:uuid>/bookmarks/', BookmarkAPIView.as_view(), name='bookmarks'),
    # favorites
    path('users/<uuid:uuid>/favorites/', FavoriteAPIView.as_view(), name='favorites'),
    # reviews
]
