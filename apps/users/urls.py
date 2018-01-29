from django.conf.urls import url

from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    KonnectMobileStatus,
    KonnectUserUpdateWithMobile,
    KonnectPasswordReset,
    OtpUpdateView
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
    url(
        r'^users/otp-update/$',
        OtpUpdateView.as_view(),
        name="api_otp_update"
    ),

    url('^users/profile', UserProfileView.as_view(), name='api_user_profile'),

    url(r'^users/konnect-mobile-status/$',
        KonnectMobileStatus.as_view(),
        name="api_konnect_mobile_status"),

    url(r'^users/konnect-user-update-with-mobile/$',
        KonnectUserUpdateWithMobile.as_view(),
        name="api_konnect_user_update_with_mobile"),

    url(r'^users/konnect-password-reset/$',
        KonnectPasswordReset.as_view(),
        name="api_konnect_password_reset"),
]
