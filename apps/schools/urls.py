from django.conf.urls import url

from schools.api_view import (
    InstitutionListView, InstitutionInfoView
)


urlpatterns = [
    url(r'^schools/list/$',
        InstitutionListView.as_view(), name='institution-list'),
    url(r'^schools/info/$',
        InstitutionInfoView.as_view(), name='institution-info'),
]