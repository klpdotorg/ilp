from common.api_views import LanguagesListView, AcademicYearView
from django.conf.urls import url, include

urlpatterns = [
    url(r'^languages/$', LanguagesListView.as_view(), name='languages'),
    url(r'^academicyear/$', AcademicYearView.as_view(), name='academicyear'),
]
