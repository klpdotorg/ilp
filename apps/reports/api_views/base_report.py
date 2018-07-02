from django.db.models import Count
from common.models import AcademicYear
from rest_framework.exceptions import ParseError


class BaseReport():

    # Returns the category wise average enrolment data
    def get_enrolment(self, categoryData):
        enrolmentdata = {"Lower Primary": {"text": "Class 1 to 4",
                                           "student_count": 0},
                         "Upper Primary": {"text": "Class 1 to 8",
                                           "student_count": 0}}
        for cat in categoryData:
            if cat in ['Lower Primary', 'Upper Primary']:
                enrolmentdata[cat]["student_count"] =\
                    categoryData[cat]["num_students"]
            if cat == 'Model Primary':
                enrolmentdata['Upper Primary']["student_count"] +=\
                    categoryData[cat]["num_students"]

        return enrolmentdata


    def get_year_comparison(self, passedid, active_schools, academic_year, year):
        comparisonData = []
        start_year = year[:2]
        end_year = year[-2:]
        prev_year = str(int(start_year)-1) + str(int(end_year)-1)
        prev_prev_year = str(int(start_year)-2) + str(int(end_year)-2)

        prev_year_id = AcademicYear.objects.get(char_id=prev_year)
        prev_prev_year_id = AcademicYear.objects.get(char_id=prev_prev_year)

        yearData = self.get_yeardata(passedid, active_schools, year, academic_year)

        prevYearData = self.get_yeardata(passedid, active_schools, prev_year,
                                         prev_year_id)
        prevPrevYearData = self.get_yeardata(passedid, active_schools,
                                             prev_prev_year, prev_prev_year_id)

        comparisonData.append(yearData)
        comparisonData.append(prevYearData)
        comparisonData.append(prevPrevYearData)

        return comparisonData



    # Throws error if mandatory parameters are missing
    def check_mandatory_params(self, mandatoryparams):
        for params in mandatoryparams:
            if not self.request.GET.get(params):
                raise ParseError("Mandatory parameter "+params+" not passed")
            else:
                if mandatoryparams[params] != [] and \
                        self.request.GET.get(params) not in\
                        mandatoryparams[params]:
                    raise ParseError("Invalid "+params+" passed,pass from the "
                                     + str(mandatoryparams[params]))

    # Returns 0 where data is None
    def check_values(self, data):
        if data["num_girls"] is None:
            data["num_girls"] = 0
        if data["num_boys"] is None:
            data["num_boys"] = 0
        if data["num_schools"] is None:
            data["num_schools"] = 0
        return data

    # Returns the number of teachers in the schools for the year
    def get_teachercount(self, active_schools, academic_year):
        teachers = active_schools.filter(
            studentgroup__staff__staffstudentgrouprelation__academic_year=academic_year
            ).aggregate(
            count=Count('studentgroup__staff__id', distinct=True))
        numteachers = teachers["count"]
        return numteachers
