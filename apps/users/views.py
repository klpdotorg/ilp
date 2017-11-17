from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from .utils import login_user, logout_user


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
                'token': token.key
            },
            status=status.HTTP_200_OK,
        )
        print (token)
        return Response({'success': 'your token will be sent to you soon!'})
