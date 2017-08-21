from common.views import ILPListAPIView, ILPViewSet
from common.models import Status, InstitutionType
from common.renderers import ILPJSONRenderer
from common.mixins import ILPStateMixin

from schools.serializers import (
    InstitutionSerializer, InstitutionInfoSerializer
)
from schools.models import Institution


class InstitutionViewSet(ILPViewSet, ILPStateMixin):
    """
    GET: Lists basic details of institutions
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    bbox_filter_field = "coord"
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

        # TODO :
        # Need to do filter for:
        # ac_year = self.request.GET.get(
        #    'academic_year', settings.DEFAULT_ACADEMIC_YEAR)
        # partner_id
        # programmes
        return qset


class InstitutionInfoViewSet(ILPViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionInfoSerializer
    # filter_class = SchoolFilter
