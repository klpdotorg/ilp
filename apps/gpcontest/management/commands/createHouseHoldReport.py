import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import ElectionBoundary, Boundary
from schools.models import Institution
from gpcontest.reports import household_report
from . import baseReport


class Command(BaseCommand, baseReport.CommonUtils):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates HouseHold Reports, pass (if no districtid or sid is passed\
            then its generated for state --districtids[commaseparated districtids]\
            surveyid startyearmonth endyearmonth \
            --sid [comma separated schoolids]'
    now = date.today()
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir+"/generated_files/householdreports/"+str(now)+"/HouseHoldReports/"
    school_out_file_prefix = "HouseHoldSchoolReport"
    templates = {"school": {"template": "HouseHold.tex", "latex": None}}
    build_d = basefiledir+"/build/"
    gpids = None
    survey = None
    surveyid = None
    gpsurveyid = None
    schoolids = None
    districtids = None
    colour = "bw"
    imagesdir = basefiledir+"/apps/gpcontest/images/"
    validqids = {138,144,145,269,147,148,149,150}

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('gpsurveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--sid', nargs='?')
        parser.add_argument('--districtid', nargs='?')
        parser.add_argument('--reportcolour', nargs='?', default='bw')

    def validateInputs(self):
        if self.gpids is not None:
            if not self.validateGPIds(self.gpids):
                return False
        if self.districtids is not None:
            if not self.validateBoundaryIds(self.districtids, 'SD'):
                return False
        if not self.validateSurveyId(self.surveyid):
            return False
        if not self.validateSurveyId(self.gpsurveyid):
            return False
        if not self.checkYearMonth(self.startyearmonth):
            return False
        if not self.checkYearMonth(self.endyearmonth):
            return False
        return True

    
    def createSchoolHouseHoldReports(self):
        schooldata = household_report.get_hh_reports_for_school_ids(self.surveyid,
                                                   self.gpsurveyid,
                                                   self.schoolids,
                                                   self.startyearmonth, 
                                                   self.endyearmonth)

        #print(schooldata)
        self.createSchoolPdfs(schooldata)

    def createHouseHoldReportBoundary(self):
        schooldata = household_report.get_hh_reports_for_districts(self.surveyid,
                                                   self.gpsurveyid,
                                                   self.districtids,
                                                   self.startyearmonth, 
                                                   self.endyearmonth)

        self.createSchoolPdfs(schooldata)

    def getYearMonth(self, yearmonth):
        return yearmonth[4:6]+"/"+yearmonth[0:4]


    def createSchoolPdfs(self, schoolsdata):
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        for schoolid in schoolsdata:
            schooldata = schoolsdata[schoolid]
            print("School Data is:")
            print(schooldata, file=self.utf8stdout)
            schoolinfo = {"district": schooldata["district_name"].capitalize(),
                          "block": schooldata["block_name"].capitalize(),
                          "schoolname": schooldata["school_name"].capitalize(),
                          "village": schooldata["village_name"].capitalize(),
                          "klpid": schoolid,
                          "disecode": schooldata["dise_code"],
                          "gpid": schooldata["gp_id"],
                          "gpname": schooldata["gp_name"].capitalize(),
                          "numparentassessments": schooldata["total_parental_assessments"],
                          "numassessments": schooldata["total_assessments"],
                          "month": self.getYearMonth(self.startyearmonth)+"-"+self.getYearMonth(self.endyearmonth)}
            compare = {"parent":schooldata["parents_perception"], "gpcontest": schooldata["gpcontest_data"]}
            assessmentinfo = []
            for question in schooldata["answers"]:
                if question["question_id"] in self.validqids:
                    assessmentinfo.append(question)
            outputdir = self.outputdir+"/"+schooldata["district_name"]+"/"+schooldata["block_name"]+"/"+schooldata["gp_name"]+"/"
            if not os.path.exists(outputdir):
                os.makedirs(outputdir)
            if not os.path.exists(self.build_d):
                os.makedirs(self.build_d)


            pdfscreated = []
            survey = {}
            survey["assessmentinfo"] = assessmentinfo
            print("Before rendering")
            renderer_template = self.templates["school"]["latex"].render(
                    info=info, schoolinfo=schoolinfo,compare=compare, survey=survey)
            print("After rendering")
            school_out_file = self.school_out_file_prefix+"_" +\
                                    str(schoolinfo["klpid"])
            print(school_out_file)
            with open(school_out_file+".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)
            os.system("xelatex -output-directory {} {}".format(
                os.path.realpath(self.build_d),
                os.path.realpath(school_out_file)))
            shutil.copy2(self.build_d+"/"+school_out_file+".pdf", outputdir)
            pdfscreated.append(os.path.realpath(self.build_d+"/" +
                                   school_out_file+".pdf"))
            self.deleteTempFiles([school_out_file+".tex"])

        self.deleteTempFiles(pdfscreated)
        return 

    def handle(self, *args, **options):
        gpids = options.get("gpid", None)
        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.gpsurveyid = options.get("gpsurveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)
        schoolids = options.get("sid", None)
        print(1)

        reportcolour = options.get("reportcolour")
        self.imagesdir = self.imagesdir+"/"+reportcolour+"/"

        if schoolids is not None:
            self.schoolids = [int(x) for x in schoolids.split(',')]

        districtids = options.get("districtid", None)
        if districtids is not None:
            self.districtids = [int(x) for x in districtids.split(',')]

        print(2)
        if not self.validateInputs():
            return
        print(3)
        self.initiatelatex()
        print(4)

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        if self.schoolids is not None:
            print("Creating School House Hold")
            self.createSchoolHouseHoldReports()
        elif self.districtids is not None:
            self.createHouseHoldReportBoundary()
        else:
            state_id=2
            districtids = Boundary.objects.filter(parent=state_id).values("id")
            self.districtids = []
            for district in districtids:
                self.districtids.append(district["id"])
            self.createHouseHoldReportBoundary()

        os.system('tar -cvf '+self.outputdir+'.tar '+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
