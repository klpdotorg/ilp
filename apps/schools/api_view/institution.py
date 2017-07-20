from django.conf import settings
from common.views import KLPListAPIView

from schools.serializers import (
    InstitutionListSerializer, InstitutionInfoSerializer
)
from common.models import Status, InstitutionType
from schools.models import Institution


class InstitutionListView(KLPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionListSerializer

    def get_queryset(self):
        qset = Institution.objects.filter(status=Status.ACTIVE)  
        s_type = self.request.GET.get('school_type', 'both')

        if s_type == 'preschools':
            qset = qset.filter(institution_type__pk=InstitutionType.PRESCHOOL)
        elif s_type == 'primaryschools':
            qset = qset.filter(
                institution_type__pk=InstitutionType.PRIMARYSCHOOL)

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
        # ac_year = self.request.GET.get(
        #     'academic_year', settings.DEFAULT_ACADEMIC_YEAR)
        # Need to do filter for:
        # geometery
        # partner_id
        # programmes
        # meeting_report
        return qset


class InstitutionInfoView(KLPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionInfoSerializer
