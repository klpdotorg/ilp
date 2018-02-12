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
    def get_counts(self, electedrepData, active_schools, academic_year):
        self.reportInfo["gender"] = {"boys": electedrepData["num_boys"],
                                     "girls": electedrepData["num_girls"]}
        self.reportInfo["school_count"] = electedrepData["num_schools"]
        self.reportInfo["student_count"] = electedrepData["num_boys"] +\
            electedrepData["num_girls"]
        self.reportInfo["teacher_count"] =\
            self.get_teachercount(active_schools, academic_year)

        if self.reportInfo["teacher_count"] == 0:
            self.reportInfo["ptr"] = "NA"
        else:
            self.reportInfo["ptr"] = round(
                self.reportInfo["student_count"] /
                float(self.reportInfo["teacher_count"]), 2)

        if self.parentInfo["schoolcount"] == 0:
            self.reportInfo["school_perc"] = 100
        else:
            self.reportInfo["school_perc"] = round(
                self.reportInfo["school_count"] *
                100 / float(self.parentInfo["schoolcount"]), 2)

    def get_parent_info(self, electedrepid):
        parent = {"schoolcount": 0}
        parentObject = ElectedrepMaster.objects.get(id=electedrepid.parent.id)
        schools = parentObject.schools()
        parent["schoolcount"] = schools.count()
        return parent

    def get_report_data(self, electedrepid):

        # Get the academic year
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1617.', 404)
        self.reportInfo["academic_year"] = year

        # Check if electedrep id is valid
        print(electedrepid)
        electedrep = ElectionBoundary.objects.get()

        print("in get summary")
        self.getSummaryData(electedrep, self.reportInfo)
        # Get list of schools associated with that electedrep
        active_schools = electedrep.schools()

        # Get aggregate data for schools with that electedrep for the current
        # academic year
        electedrepData = self.get_aggregations(active_schools, academic_year)
        electedrepData = self.check_values(electedrepData)

        # get information about the parent
        self.parentInfo = self.get_parent_info(electedrep)

        # get the counts of students/gender/teacher/school
        self.get_counts(electedrepData, active_schools, academic_year)

    def get(self, request):
        if not self.request.GET.get('id'):
            raise ParseError("Mandatory parameter id not passed")

        id = self.request.GET.get("id")
        self.get_report_data(id)
        return Response(self.reportInfo)
