from django.urls import path
from .views import PersonAPIView, DeactivatePersonAPIView


urlpatterns = [
    # profiles
    path('users/', PersonAPIView.as_view(), name='create_user'),
    path('users/whoami/', PersonAPIView.as_view(), name='get_user_info'),
    path('users/<uuid:uuid>/', PersonAPIView.as_view(), name='update_user'),
    path('users/<uuid:uuid>/deactivate/', DeactivatePersonAPIView.as_view(), name='deactivate_user'),

    # bookamarks
    # favorites
    # reviews
]
