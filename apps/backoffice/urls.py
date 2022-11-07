from django.urls import re_path
from django.views.generic import TemplateView

from backoffice.views import (
    BackOfficeView,
    GPContestValidatorView,
    BackOfficeLoginView,
    BackOfficeLogoutView
)

from backoffice.api_views import ( DataAnalysis, DataAnalysisSearch )


urlpatterns = [
    re_path(r'login/$', BackOfficeLoginView.as_view(), name='login'),
    re_path(r'logout/$', BackOfficeLogoutView.as_view(), name='logout'),
    re_path(r'export/$', BackOfficeView.as_view(), name='backoffice'),
    re_path(
        r'import/test/$',
        GPContestValidatorView.as_view(),
        name='gpcontest_validator'
    ),
    # re_path(r'analysis/$', DataAnalysisSearch.as_view(), name='search'),
    # re_path(r'/api/v1/backoffice/analysis/*', DataAnalysis.as_view(), name='analyse'),
    # re_path('', TemplateView.as_view(template_name='backoffice/index.html'), name='index'),
]
