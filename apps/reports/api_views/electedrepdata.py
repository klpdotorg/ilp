from rest_framework.response import Response
from boundary.models import ElectionBoundary, ElectionNeighbours
from common.models import AcademicYear
from . import BaseElectedRepReport
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.exceptions import APIException


class ElectedRepInfo(APIView, BaseElectedRepReport):

    reportInfo = {}

    def get_electedrep_info(self, electedrepid):
        year = self.request.GET.get('year', settings.DISE_ACADEMIC_YEAR).replace('-','')
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1415.', 404)
        self.reportInfo["academic_year"] = academic_year.year
        try:
            electedrep = ElectionBoundary.objects.get(pk=electedrepid)
        except Exception:
            raise APIException('ElectedRep id ' + electedrepid+' not found', 404)
        print(electedrep)
        self.getSummaryData(electedrep, self.reportInfo)
        self.reportInfo["neighbour_info"] = []
        neighbourlist = ElectionNeighbours.objects.filter(elect_boundary=electedrep).values_list("neighbour_id", flat=True)
        neighbours = ElectionBoundary.objects.filter(elec_comm_code__in=list(neighbourlist), const_ward_type_id=electedrep.const_ward_type_id, status_id='AC')
        if neighbours:
            self.getNeighbours(neighbours,
                               electedrep.const_ward_type, self.reportInfo)
        #self.getParentData(electedrep, self.reportInfo)
        print(self.reportInfo)

    def get(self, request):
        mandatoryparams = {'id': []}
        self.check_mandatory_params(mandatoryparams)

        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language", "english")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_electedrep_info(id)
        return Response(self.reportInfo)
