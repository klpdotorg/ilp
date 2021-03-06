from rest_framework import permissions
from rest_framework.permissions import BasePermission

from django.contrib.auth.models import Group
from boundary.models import Boundary
from schools.models import Institution
from assessments.models import QuestionGroup
import logging

logger = logging.getLogger(__name__)

# from schools.models import Institution, StudentGroup
# from boundary.models import Boundary
# from assessments.models import Assessment

class IlpBasePermission(BasePermission):
    def is_user_permitted(self, request):
        GROUPS_ALLOWED = [u'tada_admin']
        logger.info("Inside IlpBasePermission")
        if request.method in ('GET', 'HEAD','OPTIONS'):
            logger.info("User has permission to do GET")
            return True
        elif request.user.is_superuser:
            logger.info("User is a super user")
            return True
        else:
            print("User is not authenticated,is not a super user and is attempting to do a POST or PUT or DELETE or PATCH")
            return False

    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            print("User is permitted: ", self.is_user_permitted(request))
            return True
        else:
            print("User is not permitted")
            return False

class AppPostPermissions(IlpBasePermission):
    def has_permission(self, request, view):
        logger.info("inside app post permissions")
        if request.user.is_authenticated and request.method in ('GET', 'OPTIONS', 'POST'):
            logger.info("user is authenticated and can do a POST")
            return True
        else:
            return False

# # Only applicable to TADA
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


class ManageUsersPermission(BasePermission):
    def has_permission(self, request, view):
        GROUPS_ALLOWED = [u'tada_admin',u'tada_dee']
        groups = Group.objects.filter(name__in=GROUPS_ALLOWED)
        if not request.user.groups.filter(id__in=groups).exists():
            return False
        else:
            return True

            
# # Only applicable to TADA users
class InstitutionCreateUpdatePermission(IlpBasePermission):
    def has_object_permission(self, request, view, obj):
        logger.debug("Entering has_object_permission")
        if self.is_user_permitted(request):
            logger.debug("User %s is permitted to complete request", request.user)
            return True
        else:
            logger.debug("Checking if user has change_institution permission")
            hasperm = request.user.has_perm('change_institution', obj)
            print(hasperm)
            if hasperm:
                logger.debug("User has permission to change institution")
            else:
                logger.debug("User does not have permission to change institution")
            return hasperm

    def has_permission(self, request, view):
        logger.debug("Inside InstitutionCreateUpdatePermission has_permission")
        if request.method == 'OPTIONS':
            logger.debug("Request is OPTIONS. Permit this")
            return True
        elif self.is_user_permitted(request):
            logger.debug("Checking if is_user_permitted", self.is_user_permitted(request))
            return True
        elif request.method == 'POST':
            logger.debug("Attempting POST to institution endpoint")
            boundary_id = request.data.get('admin3', None)
            if boundary_id is not None:
                boundary_id = int(boundary_id)
                try:
                    boundary = Boundary.objects.get(id=boundary_id)
                except:
                    logger.error("unable to retrieve boundary object", boundary_id)
                    return False
                hasperm = request.user.has_perm('add_institution', boundary)
                logger.debug("User has request to modify institution: ", hasperm)
                return hasperm
            else:
                logger.error("Unable to retrieve admin3 or admin3 is None")
                return False
        else:
            return True


class WorkUnderInstitutionPermission(IlpBasePermission):

    def has_object_permission(self, request, view, obj):
        logger.debug("Entering has_object_permission")
        if self.is_user_permitted(request):
            logger.debug("User %s is permitted to complete request", request.user)
            return True
        else:
            logger.debug("Checking if user has crud_student_class_staff permission")
            hasperm = request.user.has_perm('crud_student_class_staff', obj.institution)
            print(hasperm)
            if hasperm:
                logger.debug("User has permission to change studetngroup")
            else:
                logger.debug("User does not have permission to change studentgroup")
            return hasperm

    def has_permission(self, request, view):
        logger.debug("Entering has_permission under WorkUnderInstitutionPermission")
        if self.is_user_permitted(request):
            if request.method == 'POST':
                institution_id = None
                #Students endpoint passes an array. hence check if data is a list and then grab institution
                if isinstance(request.data, list):
                    array = request.data[0]
                    institution_id = array['institution']
                else:
                    institution_id = request.data.get('institution', None)
                if institution_id is not None:
                    try:
                        institution = Institution.objects.get(id=int(institution_id))
                    except:
                        logger.error("Unable to retrieve institution object: ", int(institution_id))
                        return False
                    hasperm = request.user.has_perm('crud_student_class_staff', institution)
                    logger.debug("User has permission to work under institution: %s" % hasperm)
                    return hasperm
                else:
                    logger.debug("Institution ID is None")
            else:
                return True
        else:
            return False
       


class WorkUnderAssessmentPermission(IlpBasePermission):
    def has_permission(self, request, view):
        if self.is_user_permitted(request):
            return True
        else:
            print("kwargs passed to permissions is: ", view.kwargs)
            assessment_id = view.kwargs.get(
                'parent_lookup_questiongroup_id', None
            )
            try:
                assessment = QuestionGroup.objects.get(id=int(assessment_id))
            except Exception as ex:
                return False
        return request.user.has_perm('crud_answers', assessment)


class UserPermission(IlpBasePermission):
    def has_object_permission(self, request, view, obj):
        if self.is_user_permitted(request):
            return True
        else:
            return request.user.id == obj.id


class StudentRegisterPermission(BasePermission):
    def has_permission(self, request, view):
        GROUPS_ALLOWED = [u'a3_users']
        groups = Group.objects.filter(name__in=GROUPS_ALLOWED)
        if request.user.groups.filter(id__in=groups).exists():
            if request.method in ('GET', 'POST'):
                return True
        else:
            return False
