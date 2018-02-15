from django.conf.urls import url

from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    MobileValidateWithOtpView,
    OtpGenerateView,
    OtpPasswordResetView
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
        MobileValidateWithOtpView.as_view(),
        name="api_otp_update"
    ),
    url(
        r'^users/otp-generate/$',
        OtpGenerateView.as_view(),
        name="api_otp_generate"
    ),
    url(
        r'^users/otp-password-reset/$',
        OtpPasswordResetView.as_view(),
        name="api_otp_password_reset"
    ),

    url('^users/profile', UserProfileView.as_view(), name='api_user_profile'),
]
