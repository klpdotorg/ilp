from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    remove_perm
)

from schools.models import (
    Institution,
)

from boundary.models import Boundary
from assessments.models import QuestionGroup

from rest_framework.exceptions import APIException

class PermissionMixin(object):

    def get_permitted_entities(self, permitted_user, permission=None, klass=None):
        model_map = {
            'assessment':QuestionGroup,
            'boundary':Boundary,
            None:None,
        }
        
        return get_objects_for_user(
            permitted_user, permission, klass=model_map[klass]
        ).values_list('id', flat=True)

    def assign_institution_permissions(self, user_to_be_permitted, institution_id):
        try:
            institution = Institution.objects.get(id=institution_id)
        except Exception as ex:
            raise APIException(ex)
        assign_perm('change_institution', user_to_be_permitted, institution)
        assign_perm('crud_student_class_staff', user_to_be_permitted, institution)

    def assign_boundary_permissions(self, user_to_be_permitted, boundary_id):
        try:
            boundary = Boundary.objects.get(id=boundary_id)
        except Exception as ex:
            raise APIException(ex)
        print("Boundary id is: ", boundary_id)
        institutions_under_boundary = boundary.schools()
        for institution in institutions_under_boundary:
            print("Institution id is: ", institution.id)
            self.assign_institution_permissions(user_to_be_permitted, institution.id)

        child_clusters = boundary.get_clusters()
        for cluster in child_clusters:
            assign_perm('add_institution', user_to_be_permitted, cluster)

    def assign_assessment_permissions(self, user_to_be_permitted, assessment_id):
        try:
            assessment = QuestionGroup.objects.get(id=assessment_id)
        except Exception as ex:
            raise APIException(ex)
        print("Assigning crud_answers to %s " % user_to_be_permitted)
        print("Assessment id is: %s", assessment_id)
        assign_perm('crud_answers', user_to_be_permitted, assessment)

    def unassign_institution_permissions(self, user_to_be_denied, institution_id):
        try:
            institution = Institution.objects.get(id=institution_id)
        except Exception as ex:
            raise APIException(ex)
        remove_perm('change_institution', user_to_be_denied, institution)
        remove_perm('crud_student_class_staff', user_to_be_denied, institution)

    def unassign_boundary_permissions(self, user_to_be_denied, boundary_id):
        try:
            boundary = Boundary.objects.get(id=boundary_id)
        except Exception as ex:
            raise APIException(ex)

        institutions_under_boundary = boundary.get_institutions()
        for institution in institutions_under_boundary:
            self.unassign_institution_permissions(user_to_be_denied, institution.id)

        child_clusters = boundary.get_clusters()
        for cluster in child_clusters:
            remove_perm('add_institution', user_to_be_denied, cluster)

    def unassign_assessment_permissions(self, user_to_be_denied, assessment_id):
        try:
            assessment = QuestionGroup.objects.get(id=assessment_id)
        except Exception as ex:
            raise APIException(ex)
        remove_perm('crud_answers', user_to_be_denied, assessment)
