from django.urls import re_path

from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    MobileValidateWithOtpView,
    OtpGenerateView,
    OtpPasswordResetView,
    UsersViewSet,
    TadaUserLoginView,
    CheckUserRegisteredView,
    PasswordlessLoginView
)

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'tada/users', UsersViewSet, basename='tada-users')

urlpatterns = [
    re_path(
        r'^users/register/$',
        UserRegisterView.as_view(),
        name='user-register'
    ),
    re_path(
        r'^users/login/$',
        UserLoginView.as_view(),
        name='user-login'
    ),
    re_path(
        r'^users/tokenauth/$',
        PasswordlessLoginView.as_view(),
        name='passwordless-user-login'
    ),
    re_path(
        r'^users/otp-update/$',
        MobileValidateWithOtpView.as_view(),
        name="api_otp_update"
    ),
    re_path(
        r'^users/otp-generate/$',
        OtpGenerateView.as_view(),
        name="api_otp_generate"
    ),
    re_path(
        r'^users/otp-password-reset/$',
        OtpPasswordResetView.as_view(),
        name="api_otp_password_reset"
    ),
    re_path(
        r'^users/checkregistered/$',
        CheckUserRegisteredView.as_view(),
        name="api_check_registered"
    ),
    re_path('^users/profile', UserProfileView.as_view(), name='api_user_profile'),

    # TADA urls

    # re_path(
    #     r'^users/tada/register/$',
    #     TadaUserRegisterView.as_view(),
    #     name='tada-user-register'
    # ),

    re_path(
        r'^tada/users/login/$',
        TadaUserLoginView.as_view(),
        name='tada-user-login'
    ),

    # re_path(
    #     r'^users/',
    #     UsersViewSet.as_view(),
    #     name='tada-users'       
    # )
] + router.urls

app_name = "users"

