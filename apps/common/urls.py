from common.api_views import LanguagesListView
from django.conf.urls import url, include


urlpatterns = [
    url(r'^languages/$', LanguagesListView.as_view(), name='languages'),
]
