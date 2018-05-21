from django.http import Http404
from django.views.generic.detail import DetailView
from django.contrib.auth.models import Group
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from common.views import StaticPageView
from users.models import User
from users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    OtpSerializer,
    OtpGenerateSerializer,
    OtpPasswordResetSerializer
)
from users.utils import login_user
from users.permission import IsAdminOrIsSelf


class UserRegisterView(generics.CreateAPIView):
    """
    This endpoint registers a new user in ILP. Used by the
    website
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
        except Exception as e:
            raise e
        else:
            # Generate SMS pin and send OTP
            instance.generate_sms_pin()
            instance.send_otp()

            # Add user to groups
            instance.groups.add(Group.objects.get(name='ilp_auth_user'))
            instance.groups.add(Group.objects.get(name='ilp_konnect_user'))

            instance.save()


class UserLoginView(generics.GenericAPIView):
    """
    This end point logins a user by creating a token object
    """
    serializer_class = UserLoginSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = UserSerializer(serializer.user).data
        data['token'] = login_user(self.request, serializer.user).key
        return Response(data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
        Return profile fields for user matching id provided
    """
    allowed_methods = ['GET', 'PATCH']
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsSelf, permissions.IsAuthenticated, )

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class EmailVerificationView(StaticPageView):
    """
        Verifies a user's email by matching it against a token in the db.
    """

    template_name = 'email_verified.html'

    def get(self, request, **kwargs):
        email_verification_code = self.request.GET.get('token', '')
        email = self.request.GET.get('email', '')

        try:
            user = User.objects.get(
                email=email,
                email_verification_code=email_verification_code
            )
        except User.DoesNotExist:
            raise Http404
        else:
            extra_context = {}

            if user.is_email_verified:
                extra_context['already_verified'] = True
            else:
                user.email_verification_code = ''
                user.is_email_verified = True
                user.save()

            self.extra_context = extra_context
            return super(EmailVerificationView, self).get(request, **kwargs)


class ProfilePageView(DetailView):
    """
        Renders user's profile page.
    """

    model = User
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfilePageView, self).get_context_data(**kwargs)
        user = context['object']
        context['breadcrumbs'] = [
            {
                'url': '/profile/%d' % (user.id,),
                'name': 'Profile: %s %s' % (user.first_name, user.last_name,)
            }
        ]
        return context


class ProfileEditPageView(DetailView):
    """
        Renders users's profile edit page
    """

    model = User
    template_name = 'profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileEditPageView, self).get_context_data(**kwargs)
        user = context['object']
        context['breadcrumbs'] = [
            {
                'url': '/profile/%d' % (user.id,),
                'name': 'Profile'
            },
            {
                'url': '/profile/%d/edit' % (user.id,),
                'name': 'Edit'
            }
        ]
        return context


class MobileValidateWithOtpView(generics.GenericAPIView):
    """
    This end point validates a user's mobile number by matching it against
    an OTP generated during signup.
    """
    serializer_class = OtpSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        form_data = serializer.data

        try:
            user = User.objects.get(
                mobile_no=form_data['mobile_no'],
                sms_verification_pin=form_data['otp']
            )
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid Mobile/OTP'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            user.sms_verification_pin = None
            user.is_active = True
            user.is_mobile_verified = True
            user.save()
            return Response({'success': 'ok'}, status=status.HTTP_200_OK)


class OtpGenerateView(generics.GenericAPIView):
    """
    This end point generates an OTP for a mobile number that can be used by
    OtpPasswordResetView for resetting user's password
    """
    permission_classes = (
        permissions.AllowAny,
    )
    serializer_class = OtpGenerateSerializer

    def post(self, request):
        mobile_no = request.data.get('mobile_no', None)

        if mobile_no is None:
            return Response(
                {'detail': 'Mobile number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(mobile_no=mobile_no)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Mobile number not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            user.generate_sms_pin()
            user.save()
            user.send_otp()
            return Response(
                {'success': 'Otp sent'},
                status=status.HTTP_200_OK
            )


class OtpPasswordResetView(generics.GenericAPIView):
    """
    This end point accepts an users's phone number, an otp
    a password to reset the user's password.
    """
    serializer_class = OtpPasswordResetSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = OtpPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        form_data = serializer.data

        try:
            user = User.objects.get(
                mobile_no=form_data['mobile_no'],
                sms_verification_pin=form_data['otp']
            )
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid Mobile/OTP'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            user.sms_verification_pin = None
            user.set_password(form_data['password'])
            user.is_active = True
            user.is_mobile_verified = True
            user.save()
            return Response({'success': 'ok'}, status=status.HTTP_200_OK)
