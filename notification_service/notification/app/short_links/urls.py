import short_links.views as views
from django.urls import path


urlpatterns = [
    path('<short_link>/', views.ActivateUserView.as_view(), name='activate')
]
