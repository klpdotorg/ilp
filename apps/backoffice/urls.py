from django.conf.urls import url

from backoffice.views import BackOfficeView


urlpatterns = [
    url(r'$', BackOfficeView.as_view(), name='index'),
    url(r'export/$', BackOfficeView.as_view(), name='backoffice'),
]
