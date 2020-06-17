from django.conf.urls import include, url 
from ivrs.api_views import SMSView

urlpatterns = [ url(r'sms/$',SMSView.as_view(),name='api_sms'), ]

app_name = "ivrs"