from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from common.views import StaticPageView
from django.views.generic.detail import DetailView
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
    This end point login a user by creating a token object
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
        print (token)
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
