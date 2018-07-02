from rest_framework.response import Response
from boundary.models import ElectionBoundary, ElectionNeighbours
from common.models import AcademicYear
from . import BaseElectedRepReport
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.exceptions import APIException


class DemographicsElectedRepReportDetails(APIView, BaseElectedRepReport):
    '''
         This class returns the demographic report details of the elected rep
    '''
    reportInfo = {}

    def get_details_data(self, electedrep, active_schools, academic_year):
        self.reportInfo["categories"] = {}
        electionboundaryData = self.get_electionboundary_details(electedrep, academic_year)
        self.reportInfo["categories"] = electionboundaryData["cat"]
        self.reportInfo["languages"] = {"moi": {}, "mt": {}}
        self.reportInfo["languages"]["moi"] = electionboundaryData["moi"]
        self.reportInfo["languages"]["mt"] = electionboundaryData["mt"]
        self.reportInfo["enrolment"] =\
            self.get_enrolment(electionboundaryData["cat"])


    def get_report_details(self, electedrepid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1516.', 404)
        self.reportInfo["report_info"]["year"] = academic_year.year

        try:
            electedrep = ElectionBoundary.objects.get(pk=electedrepid)
        except Exception:
            raise APIException('ElectedRep id '+electedrepid+'  not found', 404)

        active_schools = electedrep.schools()
        self.get_details_data(electedrep, active_schools, academic_year)


    def get(self, request):
        mandatoryparams = {'id': []}
        self.check_mandatory_params(mandatoryparams)
        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language", "english")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_details(id)
        return Response(self.reportInfo)


class DemographicsElectedRepComparisonDetails(APIView, BaseElectedRepReport):

    '''
        Returns report comparison details
    '''
    reportInfo = {"comparison": {"year-wise": {}, "electedrep": {}}}
    totalschools = 0

    def fillComparisonData(self, electedrep, academic_year):
        data = {
            "id": electedrep.id,
            "commision_code": electedrep.elec_comm_code,
            "name": electedrep.const_ward_name,
            "type": electedrep.const_ward_type.name,
            "elected_party": electedrep.current_elected_party.name,
            "elected_rep": electedrep.current_elected_rep,
            "dise": electedrep.dise_slug,
            "avg_enrol_upper": 0,
            "avg_enrol_lower": 0,
            "ptr": 0,
            "school_count": 0,
            "school_perc": 0
            }
        active_schools = electedrep.schools()
        if active_schools.exists():
            basicData = self.get_electionboundary_basiccounts(electedrep, academic_year)
            electionboundaryData = self.get_electionboundary_details(electedrep,
                                                 academic_year)
            enrolment = self.get_enrolment(electionboundaryData["cat"])
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
            if teacher_count == 0:
                data["ptr"] = "NA"
            else:
                data["ptr"] = round(student_count / float(teacher_count), 2)
        return data


    def get_neighbour_comparison(self, academic_year, electedrep):
        comparisonData = []
        neighbourlist = ElectionNeighbours.objects.filter(elect_boundary=electedrep).values_list("neighbour_id", flat=True)
        neighbours = ElectionBoundary.objects.filter(id__in = list(neighbourlist))
        for neighbour in neighbours:
            comparisonData.append(self.fillComparisonData(neighbour,
                                                          academic_year))
        if self.totalschools != 0:
            for data in comparisonData:
                data["school_perc"] = round(
                    data["school_count"] * 100 / self.totalschools, 2)
        return comparisonData


    def get_yeardata(self,electedrep, active_schools, year, year_id):
        yeardata = {"year": year_id.year, "avg_enrol_upper": 0, "avg_enrol_lower": 0,
                    "school_count": 0}
        basicData = self.get_electionboundary_basiccounts(electedrep, year_id)
        electionData = self.get_electionboundary_details(electedrep, year_id)
        enrolment = self.get_enrolment(electionData["cat"])
        yeardata["avg_enrol_upper"] = \
            enrolment["Upper Primary"]["student_count"]
        yeardata["avg_enrol_lower"] = \
            enrolment["Lower Primary"]["student_count"]
        teacher_count = self.get_teachercount(active_schools, year_id)
        yeardata["student_count"] = basicData["num_students"]
        yeardata["teacher_count"] = teacher_count
        yeardata["school_count"] = basicData["num_schools"]

        if teacher_count == 0:
            yeardata["ptr"] = "NA"
        else:
            yeardata["ptr"] = round(basicData["num_students"]/float(teacher_count), 2)
        return yeardata


    def get_comparison_data(self, electedrep, active_schools, academic_year,
                            year):
        self.reportInfo["comparison"] = {}
        self.reportInfo["comparison"]["neighbours"] =\
            self.get_neighbour_comparison(academic_year, electedrep)
        self.reportInfo["comparison"]["year-wise"] =\
            self.get_year_comparison(electedrep, active_schools, academic_year, year)

    def get_report_comparison(self, electedrepid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1516.', 404)
        try:
            electedrep = ElectionBoundary.objects.get(pk=electedrepid)
        except Exception:
            raise APIException('ElectedRep id not found', 404)

        active_schools = electedrep.schools()
        self.get_comparison_data(electedrep, active_schools, academic_year,
                                 year)

    def get(self, request):
        mandatoryparams = {'id': []}
        self.check_mandatory_params(mandatoryparams)

        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language","english")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_comparison(id)
        return Response(self.reportInfo)
