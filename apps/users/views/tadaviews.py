import json

from django.db.models import Q
from django.contrib.auth.models import Group

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    TadaUserRegistrationSerializer,
    UserLoginSerializer,
    TadaUserSerializer
)
from users.permission import IsAdminOrIsSelf, IsAdminUser
from users.utils import login_user
from rest_framework import filters

from common.views import ILPViewSet


class UsersViewSet(viewsets.ModelViewSet):
    """
    This endpoint registers a new TADA user
    """
    permission_classes = (
        IsAdminUser,
    )
    serializer_class = TadaUserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name',)

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        if search_query:
            self.queryset = self.queryset.filter(
                Q(email=search_query) | Q(mobile_no=search_query) |
                Q(first_name=search_query) | Q(last_name=search_query)
            )
        return self.queryset.filter(is_active='True')

    def create(self, request, *args, **kwargs):
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
                print("Group name is: ", group_name)
                group_obj = Group.objects.get(name=group_name)
                print("Retrieved group object:", group_obj)
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
    
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        print("Inside TADA user update view", request.data)
        try:
            groups = data.pop("groups")
        except:
            groups = []
        instance = self.get_object()
        serializer = TadaUserSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.groups.clear()
        user.save()
        for group_name in groups:
            try:
                print("Group name is: ", group_name)
                group_obj = Group.objects.get(name=group_name)
                print("Retrieved group object:", group_obj)
            except:
                print("Did not find group")
            else:
                user.groups.add(group_obj)
        if user.is_superuser:
            user.groups.add(Group.objects.get(name='tada_admin'))
        else:
            print("Adding user to default groups")
            user.groups.add(Group.objects.get(name='ilp_auth_user'))
            user.groups.add(Group.objects.get(name='ilp_konnect_user'))
        user.save()
        print("saving user")
        response_data = TadaUserSerializer(user)
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
