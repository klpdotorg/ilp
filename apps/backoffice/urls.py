from django.conf.urls import url

from backoffice.views import BackOfficeView


urlpatterns = [
    url(r'export/$', BackOfficeView.as_view(), name='backoffice'),
]
