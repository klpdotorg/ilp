import json

from django.db.models import Q
from django.contrib.auth.models import Group

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from users.models import ( 
    User,
    UserBoundary
)
from boundary.models import (
    BoundaryStateCode
)
from users.serializers import (
    TadaUserCreateUpdateSerializer,
    UserLoginSerializer,
    TadaUserSerializer,
    PasswordSerializer,
    ChangePasswordSerializer
)
from users.permission import IsAdminOrIsSelf, IsAdminUser
from permissions.permissions import (
    HasAssignPermPermission,
    ManageUsersPermission)
from users.utils import login_user
from rest_framework import filters
from django.contrib.auth.hashers import make_password, check_password
from common.views import ILPViewSet
import logging
from rest_condition import Or

logger = logging.getLogger(__name__)

class UsersViewSet(ILPViewSet):
    """
    This endpoint registers a new TADA user
    """
    permission_classes = [
        Or(IsAdminUser, ManageUsersPermission)
    ]
    serializer_class = TadaUserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name',)
    search_fields = ('first_name', 'last_name', 'email', 'mobile_no')

    def get_queryset(self):
        try:
            search_query = self.request.query_params.get('search', None)
            role_query = self.request.query_params.get('role', 'ilp_auth_user')
            if role_query:
                self.queryset = self.queryset.filter(groups__name=role_query)
            if search_query is not None:
                self.queryset = User.objects.all().filter(
                    Q(email__icontains=search_query) |
                    Q(mobile_no__icontains=search_query) |
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query) |
                    Q(groups__name=search_query)
                )
            user = self.request.user
            if self.is_in_group(self.request.user, u'tada_dee'):
                self.queryset = self.queryset.filter(groups__name__in=["tada_dee", "tada_deo"]).filter(
                    is_active='True'
                )
            elif user.is_superuser or self.is_in_group(self.request.user, u'tada_admin'):
                self.queryset = self.queryset.filter(is_active='True')
            else:
                return None
            return self.queryset
        except Exception as e:
            print(e)


    def is_in_group(self, user, group_name):
        """
        Takes a user and a group name, and returns `True` if the user is in that group.
        """
        try:
            return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
        except Group.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            groups = data.pop("groups")
        except:
            groups=[]
        serializer = TadaUserCreateUpdateSerializer(data=data,partial=True)
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
        response_data = TadaUserSerializer(user)
        headers = self.get_success_headers(response_data.data)
        return Response(response_data.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(
        methods=['put', 'patch', 'options', 'head'], 
        serializer_class=PasswordSerializer, 
        url_path='reset-password')
    def set_password(self, request, pk=None):
        if request.method in ('OPTIONS', 'HEAD'):
            return Response({
                'name': "TADA Users Viewset",
                'description': "Method allows reset of password of a user"
            })
        else:
            serializer = PasswordSerializer(data=request.data)
            user = User.objects.get(id=pk)
            if serializer.is_valid():
                # set_password also hashes the password that the user will get
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'status': 'password set'}, status=status.HTTP_200_OK)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(
        methods=['put', 'patch', 'options', 'head'],
        serializer_class=ChangePasswordSerializer,
        url_path='change-password',
        permission_classes=((IsAdminOrIsSelf, )))
    def change_password(self, request, pk=None):
        if request.method in ('OPTIONS', 'HEAD'):
            return Response({
                'name': 'TADAUsersViewset',
                'description': 'TADA users viewset'
            })
        else:
            serializer = ChangePasswordSerializer(data=request.data)
            user = User.objects.get(id=pk)
            if serializer.is_valid():
                # set_password also hashes the password that the user will get
                old_password = serializer.data.get('old_password')
                if check_password(old_password, user.password):
                    logger.debug("Old password matches what was passed in. Proceeding with changing pwd")
                    user.set_password(serializer.data.get('new_password'))
                    user.save()
                    return Response({'status': 'password set'}, status=status.HTTP_200_OK)
                else:
                    logger.debug("Authentication Error. Existing password entered incorrectly")
                    return Response({'Authentication Error: Existing password entered incorrectly'},
                                    status = status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            groups = data.pop("groups")       
        except:
            groups = []

        # try:
        #     userboundaries = data.pop("userboundaries")
        # except:
        #     userboundaries = []

        instance = self.get_object()
        serializer = TadaUserCreateUpdateSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.groups.clear()

        user.save()
       
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

        response_data = TadaUserSerializer(user)
        headers = self.get_success_headers(response_data.data)
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

    
