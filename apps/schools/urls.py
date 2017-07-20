from django.conf.urls import url

from schools.api_view import InstitutionListView


urlpatterns = [
    url(r'^list/$', InstitutionListView.as_view()),
]