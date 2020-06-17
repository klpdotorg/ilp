from django.conf.urls import url

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
        r'^users/tokenauth/$',
        PasswordlessLoginView.as_view(),
        name='passwordless-user-login'
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
    url(
        r'^users/checkregistered/$',
        CheckUserRegisteredView.as_view(),
        name="api_check_registered"
    ),
    url('^users/profile', UserProfileView.as_view(), name='api_user_profile'),

    # TADA urls

    # url(
    #     r'^users/tada/register/$',
    #     TadaUserRegisterView.as_view(),
    #     name='tada-user-register'
    # ),

    url(
        r'^tada/users/login/$',
        TadaUserLoginView.as_view(),
        name='tada-user-login'
    ),

    # url(
    #     r'^users/',
    #     UsersViewSet.as_view(),
    #     name='tada-users'       
    # )
] + router.urls

app_name = "users"

