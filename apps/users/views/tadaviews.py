from rest_framework import generics, permissions, status
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    TadaUserRegistrationSerializer,
    UserLoginSerializer
)
from users.permission import IsAdminOrIsSelf
from django.contrib.auth.models import Group
import json

class TadaUserRegisterView(generics.CreateAPIView):
    """
    This endpoint registers a new TADA user
    """
    permission_classes =(
        permissions.AllowAny,
    )
    serializer_class = TadaUserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        print("Inside tada user register view", request.data)
        groups = data.pop("groups")
        serializer = TadaUserRegistrationSerializer(data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        for group_name in groups:
            try:
                print("Group name is: ", group_name)
                group_obj = Group.objects.get(name=group_name)
                print("Found group : ", group_obj.name)
            except:
                print("Did not find group")
            else:
                user.groups.add(group_obj)
        user.save()
        response_data = TadaUserRegistrationSerializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(response_data.data, status=status.HTTP_201_CREATED, headers=headers)

class TadaUserLoginView(generics.GenericAPIView):
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
        data = TadaUserSerializer(serializer.user).data
        data['token'] = login_user(self.request, serializer.user).key
        return Response(data, status=status.HTTP_200_OK)