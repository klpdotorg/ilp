from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import (ILPViewSet, ILPListAPIView, ILPDetailAPIView)
from common.models import Status, InstitutionType
from common.mixins import ILPStateMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from permissions.permissions import InstitutionCreateUpdatePermission
from schools.serializers import (
    InstitutionSerializer, InstitutionCreateSerializer,
    InstitutionCategorySerializer, InstitutionManagementSerializer,
    SchoolDemographicsSerializer, SchoolInfraSerializer,
    SchoolFinanceSerializer, InstitutionSummarySerializer,
    PreschoolInfraSerializer, LeanInstitutionSummarySerializer,
    InstitutionLanguageSerializer
)
from schools.models import (
    Institution, InstitutionCategory, Management, InstitutionLanguage
)
from schools.filters import InstitutionSurveyFilter
from guardian.shortcuts import (
    assign_perm,
    get_users_with_perms,
    get_objects_for_user,
)
import logging

logger = logging.getLogger(__name__)

class ProgrammeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    pass


# class InstitutionListView(ILPListAPIView):
#     queryset = Institution.objects.all()
#     serializer_class = InstitutionListSerializer
#     bbox_filter_field = "coord"

class InstitutionSummaryView(ILPStateMixin, ILPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSummarySerializer
    bbox_filter_field = "coord"
    search_fields = ('name', 'id', 'dise__school_code',)

    def get_serializer_class(self):
        lean =  self.request.GET.get('lean', False)
        print("Lean is: ", lean)
        if lean == "True" or lean == 'true':
            print("Returning lean institution serializer")
            return LeanInstitutionSummarySerializer
        else:
            return InstitutionSummarySerializer

    def get_queryset(self):
        state = self.get_state()
        qset = Institution.objects.filter(
            admin0=state, status=Status.ACTIVE
        )
        s_type = self.request.GET.get('school_type', 'both')

        # The front-end code sometimes passes in either of these. Checking both
        # for backwards compatibility
        if s_type == 'preschools' or s_type == 'pre':
            qset = qset.filter(institution_type__pk=InstitutionType.PRE_SCHOOL)
        elif s_type == 'primaryschools' or s_type == 'primary':
            qset = qset.filter(
                institution_type__pk=InstitutionType.PRIMARY_SCHOOL)
        return qset


class InstitutionViewSet(NestedViewSetMixin, ILPViewSet):
    """
    Viewset to handle institutions CRUD operations
    """
    queryset = Institution.objects.exclude(status=Status.DELETED)
    serializer_class = InstitutionSerializer
    bbox_filter_field = "coord"
    filter_backends = [InstitutionSurveyFilter, ]
    # pagination_class = LargeResultsSetPagination
    permission_classes = (InstitutionCreateUpdatePermission, )
    # filter_class = SchoolFilter

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    # def filter_queryset_by_parents_lookups(self, queryset):
    #     print("Parents query dict is: ", self.get_parents_query_dict())
    #     parents_query_dict = self.get_parents_query_dict()
    #     if parents_query_dict:
    #         try:
    #             return queryset.filter(
    #                 **parents_query_dict
    #             ).order_by().distinct('id')
    #         except ValueError:
    #             raise Http404
    #     else:
    #         print(queryset)
    #         return queryset
    
    def get_queryset(self):
        logger.debug("Fetching institutions")
        state = self.get_state()
        qset = Institution.objects.filter(
            admin0=state, status=Status.ACTIVE
        )
        s_type = self.request.GET.get('school_type', 'both')

        if s_type == 'preschools':
            qset = qset.filter(institution_type__pk=InstitutionType.PRE_SCHOOL)
        elif s_type == 'primaryschools':
            qset = qset.filter(
                institution_type__pk=InstitutionType.PRIMARY_SCHOOL)

        if self.request.GET.get('admin1', ''):
            admin1 = self.request.GET.get('admin1')
            qset = qset.filter(admin1__id=admin1)
        elif self.request.GET.get('admin2', ''):
            admin2 = self.request.GET.get('admin2')
            qset = qset.filter(admin2__id=admin2)
        elif self.request.GET.get('admin3', ''):
            admin3 = self.request.GET.get('admin3')
            qset = qset.filter(admin3__id=admin3)

        # Need to do filter for:
        # ac_year = self.request.GET.get(
        #    'academic_year', settings.DISE_ACADEMIC_YEAR)
        # partner_id
        return qset

    def create(self, request, *args, **kwargs):
        logger.debug("Inside Institution Create")
        logger.debug("Institution request data is: %s" % request.data)
        serializer = InstitutionCreateSerializer(data=request.data)
        logger.debug("Checking validity of serializer data", request.data)
        serializer.is_valid(raise_exception=True)
        institution = serializer.save()
        # self._assign_permissions(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        logger.debug("Returning response")
        return Response(
            InstitutionSerializer(institution).data,
            status=status.HTTP_201_CREATED, headers=headers
        )
    
    def _assign_permissions(self, institution):
        users_to_be_permitted = get_users_with_perms(institution.admin3)
        for user_to_be_permitted in users_to_be_permitted:
            assign_perm('change_institution', user_to_be_permitted, institution)
            assign_perm('crud_student_class_staff', user_to_be_permitted, institution)


    def update(self, request, *args, **kwargs):
        logger.debug("Entering institution update")
        try:
            instance = self.get_object()
            serializer = InstitutionCreateSerializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance, serializer.validated_data)
            instance.refresh_from_db()
            return Response(InstitutionSerializer(instance).data)
        except Exception as e:
            logger.error("Error while updating institution %s (%s)" % (e, type(e)))

    def perform_destroy(self, instance):
        logger.debug("Destroying institution ID: %s" % instance.id)
        instance.status_id = Status.DELETED
        instance.save()
        logger.debug("Institution destroyed")


class InstitutionCategoryListView(generics.ListAPIView):
    serializer_class = InstitutionCategorySerializer
    paginator = None

    def get_queryset(self):
        return InstitutionCategory.objects.all()


class InstitutionManagementListView(generics.ListAPIView):
    serializer_class = InstitutionManagementSerializer
    # paginate_by = None
    # paginate_by_param = None
    paginator = None

    def get_queryset(self):
        return Management.objects.all()


class InstitutionLanguageListView(generics.ListAPIView):
    serializer_class = InstitutionLanguageSerializer
    queryset = InstitutionLanguage.objects.all()

    def get(self, request, *args, **kwargs):
        institution_id = kwargs['pk']
        queryset = self.get_queryset().filter(institution_id=institution_id)
        return Response(self.serializer_class(queryset, many=True).data)


class InstitutionDemographics(ILPDetailAPIView):
    serializer_class = SchoolDemographicsSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return Institution.objects.filter(status='AC')


class InstitutionInfra(ILPDetailAPIView):
    # serializer_class = SchoolInfraSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'pk'

    def get_serializer_class(self):
        school_id = self.kwargs.get('pk') if hasattr(self, 'kwargs') else None
        if school_id:
            institution = Institution.objects.get(pk=school_id)
            if institution.institution_type.char_id == "pre":
                return PreschoolInfraSerializer
            else:
                return SchoolInfraSerializer

    def get_queryset(self):
        return Institution.objects.filter(status='AC')


class InstitutionFinance(ILPDetailAPIView):
    serializer_class = SchoolFinanceSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return Institution.objects.filter(status='AC')
