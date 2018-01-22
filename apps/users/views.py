from django.http import Http404
from django.views.generic.detail import DetailView
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from common.views import StaticPageView
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from .utils import login_user
from .permission import IsAdminOrIsSelf


class UserRegisterView(generics.CreateAPIView):
    """
    This endpoint registers a new user in ILP.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def perform_create(self, serializer):
        serializer.save()


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
        token = login_user(self.request, serializer.user)
        return Response(
            data={
                'token': token.key,
                'id': serializer.user.pk,
                'email': serializer.user.email,
                'firstName': serializer.user.first_name,
                'lastName': serializer.user.last_name
            },
            status=status.HTTP_200_OK,
        )
        return Response({'success': 'your token will be sent to you soon!'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
        Return profile fields for user matching id provided
    """
    allowed_methods = ['GET', 'PATCH']
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsSelf, permissions.IsAuthenticated)

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
                user.is_email_verified = True
                user.is_active = True
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


class KonnectMobileStatus(generics.GenericAPIView):
    def get(self, request):
        """
        Returns information about a mobile number - whether its a new,
        existing with/without password  dob etc
        """
        mobile_no = request.GET.get('mobile')
        try:
            user = User.objects.get(mobile_no=mobile_no)
        except User.DoesNotExist:
            return Response(
                {'action': 'signup'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            if user.password and user.dob:
                return Response({'action': 'login'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'action': 'update'},
                    status=status.HTTP_206_PARTIAL_CONTENT
                )


class KonnectUserUpdateWithMobile(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        """
        Updates user account with only mobile number.
        User by Konnect app to update those users who have already came through
        IVRS and trying to login using the app.
        """
        mobile_no = request.POST.get('mobile', '')
        dob = request.POST.get('dob', '')
        password = request.POST.get('password', '')
        source = request.POST.get('source', '')
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        user_type = request.POST.get('user_type', '')

        if not mobile_no or not dob or not password or not source:
            return Response({
                'error': 'mobile, dob, password and source are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if source != 'konnect':
            return Response({
                'error': 'invalid source'
            }, status=status.HTTP_400_BAD_REQUEST)

        if email:
            if User.objects.filter(
                    email=email).exclude(mobile_no=mobile_no).count() != 0:
                return Response({
                    'error': 'email is already registered.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            email = '%s.konnectdummy@klp.org.in' % mobile_no

        try:
            user = User.objects.get(mobile_no=mobile_no)
        except User.DoesNotExist:
            return Response(
                {'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if user.password and user.dob:
                return Response({
                    'error': 'user already has set his/her password & dob. please goto login'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.source = 'konnect'
            user.dob = dob
            user.set_password(password)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.user_type = user_type
            try:
                user.save()
            except ValidationError:
                return Response(
                    {'error': 'dob must be in YYYY-MM-DD format'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': 'user updated'})


class KonnectPasswordReset(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        """
        Password reset view for Konnect users
        Accepts mobile, dob & password.
        """
        mobile_no = request.POST.get('mobile', '')
        dob = request.POST.get('dob', '')
        password = request.POST.get('password', '')

        if not mobile_no or not dob or not password:
            return Response({
                'error': 'mobile, dob & password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(mobile_no=mobile_no, dob=dob)
        except ValidationError:
            return Response(
                {'error': 'dob must be in YYYY-MM-DD format'},
                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user.set_password(password)
            user.save()
            return Response({'success': 'Password changed'})
