from django.conf.urls import url
from django.views.generic import TemplateView

from backoffice.views import (
    BackOfficeView,
    GPContestValidatorView,
    BackOfficeLoginView
)


urlpatterns = [
    url(r'login/$', BackOfficeLoginView.as_view(), name='login'),
    url(r'export/$', BackOfficeView.as_view(), name='backoffice'),
    url(
        r'import/test/$',
        GPContestValidatorView.as_view(),
        name='gpcontest_validator'
    ),
    url('', TemplateView.as_view(template_name='backoffice/index.html'), name='index'),
]
