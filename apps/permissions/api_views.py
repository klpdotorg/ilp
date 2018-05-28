from rest_framework import permissions
from .permissions import HasAssignPermPermission
from permissions.mixins import PermissionMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status, generics, viewsets
from users.models import User

class BasicDefaultPermission(permissions.BasePermission):
    """
        Global permission check to ensure that only GET, HEAD and POST
        are allowed to ilp_auth_user and everything else is disabled
    """
    def has_permission(self, request, view):
        user = request.user
        print("user is: ", user.first_name)
        user.groups.filter(name='ilp_auth_user').exists()
        if request.user.is_authenticated and request.method in ('POST', 'GET', 'OPTIONS'):
            print("User is authenticated.PERMIT POST, GET AND HEAD")
            return True
        else:
            print("User is anonymous. PERMIT GET AND HEAD")
        return False

class PermissionView(APIView, PermissionMixin):
    permission_classes = (HasAssignPermPermission,)

    def get(self, request, pk):
        try:
            permitted_user = User.objects.get(id=pk)
        except Exception as ex:
            raise APIException(ex)

        response = {}

        response['assessments'] = self.get_permitted_entities(
            permitted_user, permission="crud_answers", klass="assessment"
        )

        response['boundaries'] = self.get_permitted_entities(
            permitted_user, permission="add_institution", klass="boundary"
        )

        response['institutions'] = self.get_permitted_entities(
            permitted_user, permission="schools.change_institution"
        )

        return Response(response)

    def post(self, request, pk):
        institution_id = self.request.data.get('institution_id', [])
        boundary_id = self.request.data.get('boundary_id', [])
        assessment_id = self.request.data.get('assessment_id', [])

        try:
            user_to_be_permitted = User.objects.get(id=pk)
        except Exception as ex:
            raise APIException(ex)

        for institution in institution_id:
            self.assign_institution_permissions(user_to_be_permitted, institution)

        for assessment in assessment_id:
            self.assign_assessment_permissions(user_to_be_permitted, assessment)

        for boundary in boundary_id:
            self.assign_boundary_permissions(user_to_be_permitted, boundary)

        return Response("Permissions assigned")

    def delete(self, request, pk):
        institution_id = self.request.data.get('institution_id', None)
        boundary_id = self.request.data.get('boundary_id', None)
        assessment_id = self.request.data.get('assessment_id', None)

        try:
            user_to_be_denied = User.objects.get(id=pk)
        except Exception as ex:
            raise APIException(ex)

        if institution_id:
            self.unassign_institution_permissions(user_to_be_denied, institution_id)

        if assessment_id:
            self.unassign_assessment_permissions(user_to_be_denied, assessment_id)

        if boundary_id:
            self.unassign_boundary_permissions(user_to_be_denied, boundary_id)

        return Response("Permissions unassigned")