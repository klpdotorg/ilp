from django.http import Http404

from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_bulk import BulkCreateModelMixin
from rest_framework.response import Response

from schools.models import (
    Student, StudentGroup, StudentStudentGroupRelation
)
from schools.serializers import (
    StudentSerializer, StudentGroupSerializer, StudentStudentGroupSerializer
)
from schools.filters import (
    StudentFilter, StudentGroupFilter
)


class StudentViewSet(
        NestedViewSetMixin,
        BulkCreateModelMixin,
        viewsets.ModelViewSet
):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_class = StudentFilter

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict.get('assessment', None):
            try:
                # assessment_id = parents_query_dict.get('assessment')
                # assessment = Assessment.objects.get(id=assessment_id)
                # studentgroups = assessment.studentgroups.all()
                return queryset.filter(
                    # studentstudentgrouprelation__student_group__in=studentgroups
                ).distinct('id')
            except Exception as ex:
                raise APIException(ex)
        elif parents_query_dict:
            try:
                return queryset.filter(
                    **parents_query_dict
                ).order_by().distinct('id')
            except ValueError:
                raise Http404
        else:
            return queryset


class StudentGroupViewSet(viewsets.ModelViewSet):
    #permission_classes = (WorkUnderInstitutionPermission,)
    #queryset = StudentGroup.objects.all()
    #print("Query set is: ", queryset)
    serializer_class = StudentGroupSerializer
    filter_class = StudentGroupFilter

    def get_queryset():
        


class StudentStudentGroupViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    pass
    queryset = StudentStudentGroupRelation.objects.all()
    serializer_class = StudentStudentGroupSerializer

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            try:
                return queryset.filter(
                    **parents_query_dict
                ).order_by().distinct('id')
            except ValueError:
                raise Http404
        else:
            return queryset

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.active = 0
#         instance.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)
