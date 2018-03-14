from rest_framework import generics, permissions, status
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    TadaUserRegistrationSerializer
)
from users.permission import IsAdminOrIsSelf
from django.contrib.auth.models import Group


class TadaUserRegisterView(generics.CreateAPIView):
    """
    This endpoint registers a new TADA user
    """
    permission_classes =(
        permissions.IsAdminUser
    )
    serializer_class = TadaUserRegistrationSerializer

    def perform_create(self,serializer):
        instance = serializer.save()
        groups = request.POST.get('groups','')
        for group in groups:
            try:
                group_name = Group.objects.get(name=group)
                print("Group name is: ", group_name.name)
            except Group.DoesNotExist:
                pass
            else:
                instance.groups.add(group_name)
                print("Added group %s to user instance", group_name.name)