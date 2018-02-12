from rest_framework.response import Response
from boundary.models import ElectionBoundary
from common.models import AcademicYear
from . import BaseBoundaryReport
from django.conf import settings
from rest_framework.views import APIView


class DemographicsElectedRepReportDetails(APIView, BaseBoundaryReport):
    '''
         This class returns the demographic report details of the elected rep
    '''

    reportInfo = {}

    def get_details_data(self, electedrepData, active_schools, academic_year):
        self.reportInfo["categories"] = {}
        for data in electedrepData["cat"]:
            self.reportInfo["categories"][data["cat"]] = {
                "school_count": data["num_schools"],
                "student_count": data["num_boys"] + data["num_girls"]}
        self.reportInfo["languages"] = {"moi": {}, "mt": {}}
        for data in electedrepData["moi"]:
            self.reportInfo["languages"]["moi"][data["moi"].upper()] =\
                {"school_count": data["num"]}
        for data in electedrepData["mt"]:
            self.reportInfo["languages"]["mt"][data["name"].upper()] =\
                {"student_count": data["num_students"]}
        self.reportInfo["enrolment"] =\
            self.get_enrolment(electedrepData["cat"])

    def get_report_details(self, electedrepid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIError('Academic year is not valid.\
                    It should be in the form of 2011-2012.', 404)
        self.reportInfo["report_info"]["year"] = year

        try:
            electedrep = ElectedrepMaster.objects.get(pk=electedrepid)
        except Exception:
            raise APIError('ElectedRep id '+electedrepid+'  not found', 404)

        active_schools = electedrep.schools()
        electedrepData = self.get_aggregations(active_schools, academic_year)
        electedrepData = self.check_values(electedrepData)
        self.get_details_data(electedrepData, active_schools, academic_year)

    def get(self, request):
        mandatoryparams = {'id': [], 'language': ['english', 'kannada']}
        self.check_mandatory_params(mandatoryparams)
        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_details(id)
        return Response(self.reportInfo)


class DemographicsElectedRepComparisonDetails(APIView, BaseBoundaryReport):

    '''
        Returns report comparison details
    '''
    reportInfo = {"comparison": {"year-wise": {}, "electedrep": {}}}
    totalschools = 0

    def fillComparison(self, electedrep, academic_year):
        data = {
            "id": electedrep.id,
            "commision_code": electedrep.elec_comm_code,
            "name": electedrep.const_ward_name.lower(),
            "type": electedrep.const_ward_type.lower(),
            "elected_party": electedrep.current_elected_party.lower(),
            "elected_rep": electedrep.current_elected_rep.lower(),
            "dise": electedrep.dise_slug,
            "avg_enrol_upper": 0,
            "avg_enrol_lower": 0,
            "ptr": 0,
            "school_count": 0,
            "school_perc": 0
            }
        active_schools = electedrep.schools()
        if active_schools.exists():
            self.totalschools += active_schools.count()
            electedrepData = self.get_aggregations(active_schools,
                                                   academic_year)
            electedrepData = self.check_values(electedrepData)
            enrolment = self.get_enrolment(electedrepData["cat"])
            data["avg_enrol_upper"] =\
                enrolment["Upper Primary"]["student_count"]
            data["avg_enrol_lower"] =\
                enrolment["Lower Primary"]["student_count"]
            data["school_count"] = electedrepData["num_schools"]
            teacher_count = self.get_teachercount(active_schools,
                                                  academic_year)
            student_count = electedrepData["num_boys"] +\
                electedrepData["num_girls"]
            data["student_count"] = student_count
            data["teacher_count"] = teacher_count
            if teacher_count == 0:
                data["ptr"] = "NA"
            else:
                data["ptr"] = round(
                    student_count / float(teacher_count), 2)
        return data

    def get_neighbour_comparison(self, academic_year, electedrep):
        comparisonData = []
        if electedrep.neighbours:
            neighbours = electedrep.neighbours.split('|')
            for neighbour in neighbours:
                try:
                    reps = ElectedrepMaster.objects.filter(
                        elec_comm_code=neighbour,
                        const_ward_type=electedrep.const_ward_type)
                except Exception:
                    raise APIError('ElectedRep neighbour id ' + neighbour +
                                   'not found', 404)
                for rep in reps:
                    comparisonData.append(self.fillComparison(rep, academic_year))
        comparisonData.append(self.fillComparison(electedrep, academic_year))
        for data in comparisonData:
            data["school_perc"] = round(data["school_count"] * 100 /
                                        float(self.totalschools), 2)
        return comparisonData

    def get_yeardata(self, active_schools, year, year_id):
        yeardata = {"year": year, "avg_enrol_upper": 0, "avg_enrol_lower": 0,
                    "school_count": 0}
        electedrepData = self.get_aggregations(active_schools, year_id)
        enrolment = self.get_enrolment(electedrepData["cat"])
        yeardata["avg_enrol_upper"] = \
            enrolment["Upper Primary"]["student_count"]
        yeardata["avg_enrol_lower"] = \
            enrolment["Lower Primary"]["student_count"]
        electedrepData = self.check_values(electedrepData)
        teacher_count = self.get_teachercount(active_schools, year_id)
        student_count = electedrepData["num_boys"] + electedrepData["num_girls"]
        yeardata["student_count"] = student_count
        yeardata["teacher_count"] = teacher_count
        yeardata["school_count"] = electedrepData["num_schools"]

        if teacher_count == 0:
            yeardata["ptr"] = "NA"
        else:
            yeardata["ptr"] = round(student_count/float(teacher_count), 2)
        return yeardata

    def get_year_comparison(self, active_schools, academic_year, year):
        comparisonData = []
        start_year = year.split('-')[0]
        end_year = year.split('-')[1]
        prev_year = str(int(start_year)-1) + "-" + str(int(end_year)-1)
        prev_prev_year = str(int(start_year)-2) + "-" + str(int(end_year)-2)

        prev_year_id = AcademicYear.objects.get(char_id=prev_year)
        prev_prev_year_id = AcademicYear.objects.get(char_id=prev_prev_year)

        yearData = {}

        prevYearData = self.get_yeardata(active_schools, prev_year,
                                         prev_year_id)
        prevPrevYearData = self.get_yeardata(active_schools,
                                             prev_prev_year, prev_prev_year_id)

        comparisonData.append(yearData)
        comparisonData.append(prevYearData)
        comparisonData.append(prevPrevYearData)

        return comparisonData

    def get_comparison_data(self, electedrep, active_schools, academic_year,
                            year):
        self.reportInfo["comparison"] = {}
        self.reportInfo["comparison"]["neighbours"] =\
            self.get_neighbour_comparison(academic_year, electedrep)
        self.reportInfo["comparison"]["year-wise"] =\
            self.get_year_comparison(active_schools, academic_year, year)

    def get_report_comparison(self, electedrepid):
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIError('Academic year is not valid.\
                    It should be in the form of 2011-2012.', 404)
        try:
            electedrep = ElectedrepMaster.objects.get(pk=electedrepid)
        except Exception:
            raise APIError('ElectedRep id not found', 404)

        active_schools = electedrep.schools()
        electedrepData = self.get_aggregations(active_schools, academic_year)
        electedrepData = self.check_values(electedrepData)
        self.get_comparison_data(electedrep, active_schools, academic_year,
                                 year)

    def get(self, request):
        mandatoryparams = {'id': [], 'language': ["english", "kannada"]}
        self.check_mandatory_params(mandatoryparams)

        id = self.request.GET.get("id")
        reportlang = self.request.GET.get("language")

        self.reportInfo["report_info"] = {"report_lang": reportlang}
        self.get_report_comparison(id)
        return Response(self.reportInfo)
