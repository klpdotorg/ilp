from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    TadaUserRegistrationSerializer,
    UserLoginSerializer,
    TadaUserSerializer
)
from users.permission import IsAdminOrIsSelf, IsAdminUser
from common.views import ILPViewSet
from django.contrib.auth.models import Group
import json
from users.utils import login_user


class UsersViewSet(viewsets.ModelViewSet):
    """
    This endpoint registers a new TADA user
    """
    permission_classes =(
        IsAdminUser,
    )
    serializer_class = TadaUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        print("Inside tada users view")
        return self.queryset.filter(is_active='True')

    def create(self, request):
        data = request.data.copy()
        print("Inside tada user register view", request.data)
        try:
            groups = data.pop("groups")
        except:
            groups=[]

        serializer = TadaUserRegistrationSerializer(data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        for group_name in groups:
            try:
                group_obj = Group.objects.get(name=group_name)
            except:
                print("Did not find group")
            else:
                user.groups.add(group_obj)
        if user.is_superuser:
            user.groups.add(Group.objects.get(name='tada_admin'))
        else:
            user.groups.add(Group.objects.get(name='ilp_auth_user'))
            user.groups.add(Group.objects.get(name='ilp_konnect_user'))
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
