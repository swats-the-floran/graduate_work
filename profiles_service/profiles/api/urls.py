from django.urls import path, include

urlpatterns = [
    path('api/users/', include('profiles.api.v1.urls'))
]
