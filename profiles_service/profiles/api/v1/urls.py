from django.urls import path
from .views import PersonAPIView, DeactivatePersonAPIView


urlpatterns = [
    path('', PersonAPIView.as_view(), name='create_user'),
    path('whoami/', PersonAPIView.as_view(), name='get_user_info'),
    path('user/<uuid:uuid>/', PersonAPIView.as_view(), name='update_user'),
    path('user/<uuid:uuid>/deactivate/', DeactivatePersonAPIView.as_view(), name='deactivate_user'),
]
