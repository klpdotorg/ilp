from rest_framework.response import Response
from boundary.models import Boundary, BoundarySchoolCategoryAgg
from common.models import AcademicYear
from . import BaseBoundaryReport
from rest_framework.exceptions import ParseError
from django.conf import settings
from django.db.models import Sum
from rest_framework.views import APIView


class BoundarySummaryReport(APIView, BaseBoundaryReport):
    '''
        Returns report summary
    '''
    reportInfo = {"report_info": {}}
    parentInfo = {}

    # filling the counts in the data structure to be returned
    def get_counts(self, boundary, active_schools, academic_year):
        basiccounts = self.get_boundary_basiccounts(boundary, academic_year)
        self.reportInfo["gender"] = {"boys": basiccounts["gender"]["boys"],
                                     "girls": basiccounts["gender"]["girls"]}
        self.reportInfo["student_count"] = basiccounts["num_students"]
        self.reportInfo["school_count"] = basiccounts["num_schools"]
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

    def get_boundary_data(self, boundaryid):

        # Get the academic year
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIError('Academic year is not valid.\
                    It should be in the form of 2011-2012.', 404)
        self.reportInfo["academic_year"] = academic_year.year

        # Check if boundary id is valid
        try:
            boundary = Boundary.objects.get(pk=boundaryid)
        except Exception:
            raise APIError('Boundary not found', 404)

        # Get list of schools associated with that boundary
        active_schools = boundary.schools()

        # get information about the parent
        self.parentInfo = self.get_parent_info(boundary)

        # get the summary data
        self.get_boundary_summary_data(boundary, self.reportInfo)

        # get the counts of students/gender/teacher/school
        self.get_counts(boundary, active_schools, academic_year)

    def get(self, request):
        if not self.request.GET.get('id'):
            raise ParseError("Mandatory parameter id not passed")

        id = self.request.GET.get("id")
        self.get_boundary_data(id)
        return Response(self.reportInfo)
