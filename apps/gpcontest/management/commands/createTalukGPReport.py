import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import Boundary
from gpcontest.reports import generate_report, school_compute_numbers, generate_boundary_reports
from . import baseReport


class Command(BaseCommand, baseReport.CommonUtils):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates Taluk Reports, pass surveyid startyearmonth endyearmonth\
            --talukid talukid [comma separated talukids]'
    assessmentorder = ["class4", "class5", "class6"]
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
    sendto = {"taluk": {
        "executiveofficer": {"langname": "ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು", "name": "Panchayath Executive Officer"},
        "talukeducationofficer": {"langname": "ಕ್ಷೇತ್ರ ಶಿಕ್ಷಣಾಧಿಕಾರಿಗಳು", "name": "Block Education Officer"},
        "bdo": {"langname": "", "name": "Block Development Officer"},
        "mla": {"langname": " ಮಾನ್ಯ ಶಾಸಕರು", "name": "Honorable MLA"},
        "president": {"langname": "ತಾಲೂಕು ಪಂಚಾಯತಿ ಅಧ್ಯಕ್ಷರು", "name": "Block Panchayat President"},
        "brc": {"langname": "ಕ್ಷೇತ್ರ ಸಮನ್ವಯಾಧಿಕಾರಿಗಳು", "name": "Block Resource Centers"}}
        }
    now = date.today()
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir + "/generated_files/gpreports/" + str(now) + "/BoundaryReports/"
    talukoutputdir = "talukreports"
    taluk_out_file_prefix = "TalukGPReport"

    templates = {"taluk": {"template": "TalukGPReport.tex", "latex": None}}

    build_d = basefiledir + "/build/"
    survey = None
    surveyid = None
    taluk = {}
    talukids = None
    colour = "bw"
    imagesdir = basefiledir + "/apps/gpcontest/images/"
    translatedmonth = {
        'kannada': {1: 'ಜನವರಿ', 2: 'ಫೆಬ್ರವರಿ', 3: 'ಮಾರ್ಚ್', 4: 'ಎಪ್ರಿಲ್', 5: 'ಮೇ', 6: 'ಜೂನ್', 7: 'ಜುಲೈ', 8: 'ಆಗಸ್ಟ್',
                    9: 'ಸೆಪ್ಟಂಬರ್', 10: 'ಅಕ್ಟೋಬರ್', 11: 'ನವೆಂಬರ್', 12: 'ಡಿಸೆಂಬರ್'},
        'english': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                    9: 'September',
                    10: 'October', 11: 'November', 12: 'December'}}
    language = 'kannada'

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--talukid', nargs='?')
        parser.add_argument('--reportcolour', nargs='?', default='bw')
        parser.add_argument('--lang', nargs='?', default='kannada')

    def validateInputs(self):
        if self.talukids is not None:
            if not self.validateBoundaryIds(self.talukids, 'TA'):
                return False
        if not self.validateSurveyId(self.surveyid):
            return False

        if not self.checkYearMonth(self.startyearmonth):
            return False
        if not self.checkYearMonth(self.endyearmonth):
            return False
        return True
    def createtalukPdfs(self, talukid, talukdata, outputdir, build_dir):
        template = self.templates["taluk"]["latex"]

        if talukdata["parent_langname"] == "" or talukdata["parent_langname"] == None:
            districtname = talukdata["parent_boundary_name"].capitalize()
        else:
            districtname = "(" + talukdata["parent_boundary_name"].capitalize() + ")"

        if talukdata["boundary_langname"] == "" or talukdata["boundary_langname"] == None:
            talukname = talukdata["boundary_name"].capitalize()
        else:
            talukname = "(" + talukdata["boundary_name"].capitalize() + ")"

        if talukdata["boundary_langname"].startswith('"') and talukdata["boundary_langname"].endswith('"'):
            talukdata["boundary_langname"] = talukdata["boundary_langname"][1:-1]
        elif talukdata["boundary_langname"].startswith("'") and talukdata["boundary_langname"].endswith("'"):
            talukdata["boundary_langname"] = talukdata["boundary_langname"][1:-1]
        else :
            talukdata["boundary_langname"] = talukdata["boundary_langname"]

        talukinfo = {"talukname": talukname,
                     "taluk_langname": talukdata["boundary_langname"],
                     "districtname": districtname,
                     "district_langname": talukdata["parent_langname"],
                     "num_gps": talukdata["num_gps"],
                     "school_count": talukdata["num_schools"],
                     "totalstudents": talukdata["num_students"]}
        assessmentinfo = []
        for assessment in self.assessmentorder:
            if self.assessmentnames[assessment]["name"] in talukdata:
                talukdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(talukdata[self.assessmentnames[assessment]["name"]])
        year, month = self.getYearMonth(str(self.now))
        info = {"imagesdir": self.imagesdir, "acadyear": self.academicyear, "year": year, "month": month}
        percent_scores = {}
        if "percent_scores" not in talukdata:
            percent_scores = None
        else:
            for assessment in talukdata["percent_scores"]:
                numcompetency = 0
                for competency in talukdata["percent_scores"][assessment]:
                    if talukdata["percent_scores"][assessment][competency] == 'NA':
                        continue
                    numcompetency += 1
                    if percent_scores == {}:
                        percent_scores["assessments"] = {}
                    if assessment in percent_scores["assessments"]:
                        percent_scores["assessments"][assessment][competency] = talukdata["percent_scores"][assessment][
                            competency]
                    else:
                        percent_scores["assessments"][assessment] = {
                            competency: talukdata["percent_scores"][assessment][competency]}
            percent_scores["num_competencies"] = numcompetency

        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        for sendto in self.sendto["taluk"]:
            renderer_template = template.render(talukinfo=talukinfo,
                                                assessmentinfo=assessmentinfo,
                                                info=info,
                                                percent_scores=percent_scores,
                                                sendto=self.sendto["taluk"][sendto])

            output_file = self.taluk_out_file_prefix + "_" + str(talukid) + "_" + sendto

            with open(output_file + ".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)

            os.system("xelatex -output-directory {} {}".format(
                os.path.realpath(build_dir),
                os.path.realpath(output_file)))
            shutil.copy2(build_dir + "/" + output_file + ".pdf", outputdir)
            self.deleteTempFiles([output_file + ".tex",
                                  build_dir + "/" + output_file + ".pdf"])
        return outputdir

    def getYearMonth(self, inputdate):
        print(inputdate)
        year = int(inputdate[0:4])
        month = self.translatedmonth[self.language][int(inputdate[5:7])]
        return year, month

    def createtalukReports(self):
        print(self.talukids)
        taluk_outputdir = self.outputdir + "/taluks/"
        talukinfo = generate_boundary_reports.generate_boundary_reports(
            self.surveyid, self.talukids, self.startyearmonth,
            self.endyearmonth)

        for taluk in talukinfo:
            taluk_builddir = self.build_d + str(self.now) + \
                             "/taluks/" + str(taluk)
            self.createtalukPdfs(taluk, talukinfo[taluk], taluk_outputdir,
                                 taluk_builddir)

    def handle(self, *args, **options):
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)
        talukids = options.get("talukid", None)

        self.language = options.get("lang")
        self.templatedir = self.templatedir + "/" + self.language + "/"
        self.imagesdir = self.imagesdir + "/" + self.language + "/"

        reportcolour = options.get("reportcolour")
        self.imagesdir = self.imagesdir + "/" + reportcolour + "/"

        print(self.imagesdir)

        if talukids is not None:
            self.talukids = [int(x) for x in talukids.split(',')]

        if not self.validateInputs():
            return
        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        if self.talukids is not None:
            print(talukids)
            self.createtalukReports()

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
