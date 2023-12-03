from django.urls import path, include

urlpatterns = [
    path('v1/', include('profiles.api.v1.urls'))
]
