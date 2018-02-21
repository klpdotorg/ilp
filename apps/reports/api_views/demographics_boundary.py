from rest_framework.response import Response
from boundary.models import Boundary, BoundaryNeighbours
from common.models import AcademicYear
from . import BaseBoundaryReport
from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.exceptions import APIException


class DemographicsBoundaryReportDetails(APIView, BaseBoundaryReport):
    '''
    This class returns the demographic report details
    '''
    reportInfo = {}

    def get_details_data(self, boundary, active_schools, academic_year):
        self.reportInfo["categories"] = {}
        boundaryData = self.get_boundary_details(boundary, academic_year)
        self.reportInfo["categories"] = boundaryData["cat"]
        self.reportInfo["languages"] = {"moi": {}, "mt": {}}
        self.reportInfo["languages"]["moi"] = boundaryData["moi"]
        self.reportInfo["languages"]["mt"] = boundaryData["mt"]
        self.reportInfo["enrolment"] =\
            self.get_enrolment(boundaryData["cat"])

    def get_report_details(self, boundaryid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1415.', 404)
        self.reportInfo["report_info"]["year"] = academic_year.year

        try:
            boundary = Boundary.objects.get(pk=boundaryid)
        except Exception:
            raise APIException('Boundary not found', 404)

        active_schools = boundary.schools()
        self.get_details_data(boundary, active_schools, academic_year)

    def get(self, request):
        mandatoryparams = {'id': []}
        self.check_mandatory_params(mandatoryparams)
        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language", "english")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_details(id)
        return Response(self.reportInfo)


class DemographicsBoundaryComparisonDetails(APIView, BaseBoundaryReport):

    '''
        Returns report comparison details
    '''
    reportInfo = {"comparison": {"year-wise": {}, "neighbours": {}}}

    parentInfo = {}

    totalschools = 0

    def get_yeardata(self, boundary, active_schools, year, year_id):
        yeardata = {"year": year_id.year, "avg_enrol_upper": 0, "avg_enrol_lower": 0,
                    "school_count": 0}
        basicData = self.get_boundary_basiccounts(boundary, year_id)
        boundaryData = self.get_boundary_details(boundary, year_id)
        enrolment = self.get_enrolment(boundaryData["cat"])
        yeardata["avg_enrol_upper"] = \
            enrolment["Upper Primary"]["student_count"]
        yeardata["avg_enrol_lower"] = \
            enrolment["Lower Primary"]["student_count"]
        #boundaryData = self.check_values(boundaryData)
        teacher_count = self.get_teachercount(active_schools, year_id)
        yeardata["student_count"] = basicData["num_students"]
        yeardata["teacher_count"] = teacher_count
        yeardata["school_count"] = basicData["num_schools"]

        if teacher_count == 0:
            yeardata["ptr"] = "NA"
        else:
            yeardata["ptr"] = round(basicData["num_students"]/float(teacher_count), 2)
        return yeardata

    def fillComparisonData(self, boundary, academic_year):
        data = {"name": boundary.name,
                "id": boundary.id,
                "type": boundary.boundary_type.name,
                "avg_enrol_upper": 0,
                "avg_enrol_lower": 0,
                "ptr": 0,
                "school_count": 0,
                "school_perc": 0}
        active_schools = boundary.schools()
        if active_schools.exists():
            basicData = self.get_boundary_basiccounts(boundary, academic_year)
            boundaryData = self.get_boundary_details(boundary,
                                                 academic_year)
            #boundaryData = self.check_values(boundaryData)
            enrolment = self.get_enrolment(boundaryData["cat"])
            data["avg_enrol_upper"] =\
                enrolment["Upper Primary"]["student_count"]
            data["avg_enrol_lower"] =\
                enrolment["Lower Primary"]["student_count"]
            data["school_count"] = basicData["num_schools"]
            teacher_count = self.get_teachercount(active_schools,
                                                  academic_year)
            student_count = basicData["num_students"]
            data["student_count"] = student_count
            data["teacher_count"] = teacher_count
            if boundary.boundary_type.name == 'SD':
                self.totalschools += data["school_count"]
            else:
                parentInfo = self.get_parent_info(boundary)
                data["school_perc"] = round(
                    basicData["num_schools"] * 100 /
                    float(parentInfo["schoolcount"]), 2)
            if teacher_count == 0:
                data["ptr"] = "NA"
            else:
                data["ptr"] = round(student_count / float(teacher_count), 2)
        return data

    def get_boundary_comparison(self, academic_year, boundary):
        comparisonData = []
        neighbourlist = BoundaryNeighbours.objects.filter(boundary=boundary).values_list("neighbour_id", flat=True)
        neighbours = Boundary.objects.filter(id__in = list(neighbourlist))
        for neighbour in neighbours:
            comparisonData.append(self.fillComparisonData(neighbour,
                                                          academic_year))
        if self.totalschools != 0:
            for data in comparisonData:
                data["school_perc"] = round(
                    data["school_count"] * 100 / self.totalschools, 2)
        return comparisonData

    def get_comparison_data(self, boundary, active_schools, academic_year, year):
        self.parentInfo = self.get_parent_info(boundary)
        self.reportInfo["parent"] = self.parentInfo
        self.reportInfo["comparison"] = {}
        self.reportInfo["comparison"]["year-wise"] =\
            self.get_year_comparison(boundary, active_schools, academic_year, year)
        self.reportInfo["comparison"]["neighbours"] =\
            self.get_boundary_comparison(academic_year, boundary)

    def get_report_comparison(self, boundaryid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1415.', 404)
        try:
            boundary = Boundary.objects.get(pk=boundaryid)
        except Exception:
            raise APIException('Boundary not found', 404)

        active_schools = boundary.schools()
        self.get_comparison_data(boundary, active_schools, academic_year,
                                 year)

    def get(self, request):
        mandatoryparams = {'id': []}
        self.check_mandatory_params(mandatoryparams)

        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language", "english")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_comparison(id)
        return Response(self.reportInfo)
