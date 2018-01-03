from django.conf.urls import url

from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    KonnectMobileStatus
)

urlpatterns = [
    url(
        r'^users/register/$',
        UserRegisterView.as_view(),
        name='user-register'
    ),
    url(
        r'^users/login/$',
        UserLoginView.as_view(),
        name='user-login'
    ),

    url('^users/profile', UserProfileView.as_view(), name='api_user_profile'),

    url(r'^users/konnect-mobile-status/$',
        KonnectMobileStatus.as_view(),
        name="konnect_mobile_status"),
]
