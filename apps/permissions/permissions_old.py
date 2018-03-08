from rest_framework import permissions
from rest_framework.permissions import BasePermission

from django.contrib.auth.models import Group

from schools.models import Institution, StudentGroup
from boundary.models import Boundary
from assessments.models import Assessment

class IlpBasePermission(BasePermission):
    def is_user_permitted(self, request):
        GROUPS_ALLOWED = [u'tada_admin']
        #groups = Group.objects.filter(name__in=GROUPS_ALLOWED)

        #if request.method in permissions.SAFE_METHODS:
        if request.user.is_authenticated and request.method in ('GET', 'POST', 'OPTIONS'):
            print("User is authenticated and method is one of GET, POST, OPTIONS")
            return True
        elif request.user.is_superuser:
            print("User is a super user")
            return True
        # elif request.user.groups.filter(id__in=groups).exists():
        #     return True
        else:
            return False

    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            return True
        else:
            return False


# Only applicable to TADA
class HasAssignPermPermission(BasePermission):
    def has_permission(self, request, view):
        GROUPS_ALLOWED = [u'tada_admin',u'tada_dee']
        groups = Group.objects.filter(name__in=GROUPS_ALLOWED)

        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            return True
        elif not request.user.groups.filter(id__in=groups).exists():
            return False
        else:
            return True


# Only applicable to TADA users
class InstitutionCreateUpdatePermission(IlpBasePermission):
    def has_object_permission(self, request, view, obj):
        if self.is_user_permitted(request):
            return True
        else:
            return request.user.has_perm('change_institution', obj)

    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            return True
        elif request.method == 'POST':
            boundary_id = request.data.get('boundary', None)
            try:
                boundary = Boundary.objects.get(id=boundary_id)
            except:
                return False
            return request.user.has_perm('add_institution', boundary)
        else:
            return True


class WorkUnderInstitutionPermission(IlpBasePermission):
    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            return True
        else:
            institution_id = request.data.get('institution', None)
            try:
                institution = Institution.objects.get(id=institution_id)
            except:
                return False
        return request.user.has_perm('crud_student_class_staff', institution)


class WorkUnderAssessmentPermission(IlpBasePermission):
    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            return True
        else:
            assessment_id = view.kwargs.get(
                'parent_lookup_student__studentgroup__asssessment', None
            )
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Exception as ex:
                return False
        return request.user.has_perm('crud_answers', assessment)


class UserPermission(IlpBasePermission):
    def has_object_permission(self, request, view, obj):
        if self.is_user_permitted(request):
            return True
        else:
            return request.user.id == obj.id
