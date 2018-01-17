from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import (ILPViewSet, ILPListAPIView, ILPDetailAPIView)
from common.models import Status, InstitutionType
from common.mixins import ILPStateMixin

from schools.serializers import (
    InstitutionSerializer, InstitutionCreateSerializer,
    InstitutionCategorySerializer, InstitutionManagementSerializer,
    SchoolDemographicsSerializer, SchoolInfraSerializer,
    SchoolFinanceSerializer, InstitutionSummarySerializer,
    PreschoolInfraSerializer, LeanInstitutionSummarySerializer
)
from schools.models import (
    Institution, InstitutionCategory, Management
)
from schools.filters import InstitutionSurveyFilter


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

    # def get_serializer_class(self):
    #     school_id =  self.kwargs.get('lean') if hasattr(self, 'kwargs') else None
    #     if school_id:
    #         institution = Institution.objects.get(pk=school_id)
    #         if institution.institution_type.char_id == "pre":
    #             return PreschoolInfraSerializer
    #         else:
    #             return SchoolInfraSerializer
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


class InstitutionViewSet(ILPViewSet):
    """
    GET: Lists basic details of institutions
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    bbox_filter_field = "coord"
    filter_backends = [InstitutionSurveyFilter, ]
    # pagination_class = LargeResultsSetPagination
    # renderer_classes = (ILPJSONRenderer, )
    # filter_class = SchoolFilter

    def get_queryset(self):
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
        #    'academic_year', settings.DEFAULT_ACADEMIC_YEAR)
        # partner_id
        return qset

    def create(self, request, *args, **kwargs):
        serializer = InstitutionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = serializer.save()
        # todo self._assign_permissions(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            InstitutionCreateSerializer(institution).data,
            status=status.HTTP_201_CREATED, headers=headers
        )


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
        school_id =  self.kwargs.get('pk') if hasattr(self, 'kwargs') else None
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
