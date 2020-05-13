from django.conf.urls import url
from django.views.generic import TemplateView

from backoffice.views import (
    BackOfficeView,
    GPContestValidatorView,
    BackOfficeLoginView,
    BackOfficeLogoutView
)

from backoffice.api_views import ( DataAnalysis, DataAnalysisSearch )


urlpatterns = [
    url(r'login/$', BackOfficeLoginView.as_view(), name='login'),
    url(r'logout/$', BackOfficeLogoutView.as_view(), name='logout'),
    url(r'export/$', BackOfficeView.as_view(), name='backoffice'),
    url(
        r'import/test/$',
        GPContestValidatorView.as_view(),
        name='gpcontest_validator'
    ),
    url(r'analysis/$', DataAnalysisSearch.as_view(), name='search'),
    url(r'/api/v1/backoffice/analysis/*', DataAnalysis.as_view(), name='analyse'),
    url('', TemplateView.as_view(template_name='backoffice/index.html'), name='index'),
]
