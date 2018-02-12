from rest_framework.response import Response
from boundary.models import ElectionBoundary
from common.models import AcademicYear
from . import BaseElectedRepReport
from django.conf import settings
from rest_framework.views import APIView


class ElectedRepInfo(APIView, BaseElectedRepReport):

    reportInfo = {}

    def get_electedrep_info(self, electedrepid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIError('Academic year is not valid.\
                    It should be in the form of 2011-2012.', 404)
        self.reportInfo["academic_year"] = year
        try:
            electedrep = ElectedrepMaster.objects.get(pk=electedrepid)
        except Exception:
            raise APIError('ElectedRep id ' + electedrepid+' not found', 404)
        self.getSummaryData(electedrep, self.reportInfo)
        self.reportInfo["neighbour_info"] = []
        if electedrep.neighbours:
            self.getNeighbours(electedrep.neighbours.split('|'),
                               electedrep.const_ward_type, self.reportInfo)
        self.getParentData(electedrep, self.reportInfo)

    def get(self, request):
        mandatoryparams = {'id': [], 'language': ["english", "kannada"]}
        self.check_mandatory_params(mandatoryparams)

        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_electedrep_info(id)
        return Response(self.reportInfo)
