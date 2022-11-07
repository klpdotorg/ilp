from django.urls import re_path, include
from ivrs.api_views import SMSView

urlpatterns = [ re_path(r'sms/$',SMSView.as_view(),name='api_sms'), ]

app_name = "ivrs"