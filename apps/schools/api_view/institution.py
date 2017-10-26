from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import ILPViewSet
from common.models import Status, InstitutionType
from common.renderers import ILPJSONRenderer
from common.mixins import ILPStateMixin
from common.pagination import LargeResultsSetPagination

from schools.serializers import (
    InstitutionSerializer, InstitutionInfoSerializer,
    InstitutionCreateSerializer
)
from schools.models import Institution


class ProgrammeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    pass


class InstitutionViewSet(ILPViewSet, ILPStateMixin):
    """
    GET: Lists basic details of institutions
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    bbox_filter_field = "coord"
    pagination_class = LargeResultsSetPagination
    renderer_classes = (ILPJSONRenderer, )
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

        # TODO
        # Need to do filter for:
        # ac_year = self.request.GET.get(
        #    'academic_year', settings.DEFAULT_ACADEMIC_YEAR)
        # partner_id
        # programmes
        return qset

    def create(self, request, *args, **kwargs):
        serializer = InstitutionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # TODO
        # self._assign_permissions(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class InstitutionInfoViewSet(ILPViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionInfoSerializer
    # filter_class = SchoolFilter
