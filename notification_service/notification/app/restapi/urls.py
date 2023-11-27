from django.urls import include, path


urlpatterns = [
    path('v1/notify/', include('restapi.v1.urls')),
]
