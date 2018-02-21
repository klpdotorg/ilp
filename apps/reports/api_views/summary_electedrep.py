from rest_framework.response import Response
from boundary.models import ElectionBoundary
from common.models import AcademicYear
from . import BaseElectedRepReport
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from django.conf import settings
from rest_framework.views import APIView


class ElectedRepSummaryReport(APIView, BaseElectedRepReport):
    '''
        Returns report summary
    '''
    reportInfo = {}
    parentInfo = {}

    # filling the counts in the data structure to be returned
    def get_counts(self, electedrep, active_schools, academic_year):
        electedrepData = self.get_electionboundary_basiccounts(electedrep, academic_year)
        print(electedrepData)
        self.reportInfo["gender"] = electedrepData["gender"]
        self.reportInfo["school_count"] = electedrepData["num_schools"]
        self.reportInfo["student_count"] = electedrepData["num_students"]
        self.reportInfo["teacher_count"] =\
            self.get_teachercount(active_schools, academic_year)

        if self.reportInfo["teacher_count"] == 0:
            self.reportInfo["ptr"] = "NA"
        else:
            self.reportInfo["ptr"] = round(
                self.reportInfo["student_count"] /
                float(self.reportInfo["teacher_count"]), 2)


    def get_report_data(self, electedrepid):

        # Get the academic year
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1617.', 404)
        self.reportInfo["academic_year"] = academic_year.year

        # Check if electedrep id is valid
        electedrep = ElectionBoundary.objects.get(pk=electedrepid)

        print("in get summary")
        self.getSummaryData(electedrep, self.reportInfo)
        # Get list of schools associated with that electedrep
        active_schools = electedrep.schools()

        # get the counts of students/gender/teacher/school
        self.get_counts(electedrep, active_schools, academic_year)

    def get(self, request):
        if not self.request.GET.get('id'):
            raise ParseError("Mandatory parameter id not passed")

        id = self.request.GET.get("id")
        self.get_report_data(id)
        return Response(self.reportInfo)
