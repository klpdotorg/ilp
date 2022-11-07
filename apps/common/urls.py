from common.api_views import (
    LanguagesListView, AcademicYearView,
    RespondentTypeView
)
from django.urls import re_path, include

urlpatterns = [
    re_path(r'^languages/$', LanguagesListView.as_view(), name='languages'),
    re_path(r'^academicyear/$', AcademicYearView.as_view(), name='academicyear'),
    re_path(r'^respondenttype/$', RespondentTypeView.as_view(), name='respondenttype')
]

app_name = "common"
