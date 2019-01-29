from django.conf.urls import url

from backoffice.views import (
    BackOfficeView,
    GPContestValidatorView
)


urlpatterns = [
    # url(r'$', BackOfficeView.as_view(), name='index'),
    url(r'export/$', BackOfficeView.as_view(), name='backoffice'),
    url(
        r'import/test/$',
        GPContestValidatorView.as_view(),
        name='gpcontest_validator'
    ),
]
