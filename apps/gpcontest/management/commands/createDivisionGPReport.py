import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import Boundary
from gpcontest.reports import generate_boundary_reports
from . import baseReport


class Command(BaseCommand, baseReport.CommonUtils):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates Division Reports, pass surveyid startyearmonth endyearmonth\
            --divisionid [commaseparated divisionids]'
    assessmentorder = ["class4", "class5", "class6"]
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
    sendto = {
        "division": {
            "HonorableCommissioners": {"langname": "ಮಾನ್ಯ ಆಯುಕ್ತರು ", "name": "Honorable Commissioners"},
            }}
    now = date.today()
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir + "/generated_files/gpreports/" + str(now) + "/BoundaryReports/"
    divisionutputdir = "divisionreports"
    division_out_file_prefix = "DivisionGPReport"

    districtsummary = []

    templates = {"division": {"template": "DivisionGPReport.tex", "latex": None}}

    build_d = basefiledir + "/build/"
    divison = {}
    survey = None
    divisionids = None
    surveyid = None
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
        parser.add_argument('--divisionid', nargs='?')
        parser.add_argument('--reportcolour', nargs='?', default='bw')
        parser.add_argument('--lang', nargs='?', default='kannada')

    def validateInputs(self):
        if self.divisionids is not None:
            if not self.validateBoundaryIds(self.divisionids, 'DV'):
                return False
        if not self.validateSurveyId(self.surveyid):
            return False

        if not self.checkYearMonth(self.startyearmonth):
            return False
        if not self.checkYearMonth(self.endyearmonth):
            return False
        return True

    def createDivisionReports(self):
        data = {}
        data["division_info"] = {}
        data["division_info"] = generate_boundary_reports.generate_boundary_reports(
            self.surveyid, self.divisionids, self.startyearmonth,
            self.endyearmonth)

        for division in data["division_info"]:
            outputdir = self.createDivisionPdfs(division,data["division_info"][division])
    def createDivisionPdfs(self, divisionid, divisiondata):
        template = self.templates["division"]["latex"]
        if type(divisiondata) is int or type(divisiondata) is str:
            return
        print("divisiondata", divisiondata)
        if divisiondata["boundary_langname"] == "" or divisiondata["boundary_langname"] == None:
            divisionname = divisiondata["boundary_name"].capitalize()
        else:
            divisionname = "(" + divisiondata["boundary_name"].capitalize() + ")"

        divisioninfo = {"name": divisionname,
                        "langname": divisiondata["boundary_langname"],
                        "num_districts": divisiondata["num_districts"],
                        "num_blocks": divisiondata["num_blocks"],
                        "num_gps": divisiondata["num_gps"],
                        "num_schools": divisiondata["num_schools"],
                        "totalstudents": divisiondata["num_students"]}
        print("division info", divisioninfo)
        assessmentinfo = []
        for assessment in self.assessmentorder:
            if self.assessmentnames[assessment]["name"] in divisiondata:
                divisiondata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment][
                    "class"]
                assessmentinfo.append(divisiondata[self.assessmentnames[assessment]["name"]])
        year, month = self.getYearMonth(str(self.now))
        info = {"imagesdir": self.imagesdir, "acadyear": self.academicyear, "year": year, "month": month}
        print("info month", info)
        percent_scores = {}
        if "percent_scores" not in divisiondata:
            percent_scores = None
        else:
            for assessment in divisiondata["percent_scores"]:
                numcompetency = 0
                for competency in divisiondata["percent_scores"][assessment]:
                    if divisiondata["percent_scores"][assessment][competency] == 'NA':
                        continue
                    numcompetency += 1
                    if percent_scores == {}:
                        percent_scores["assessments"] = {}
                    if assessment in percent_scores["assessments"]:
                        percent_scores["assessments"][assessment][competency] = \
                        divisiondata["percent_scores"][assessment][competency]
                    else:
                        percent_scores["assessments"][assessment] = {
                            competency: divisiondata["percent_scores"][assessment][competency]}
            percent_scores["num_competencies"] = numcompetency

        outputdir = self.outputdir + "/divisions/" + str(divisionid)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        for sendto in self.sendto["division"]:
            renderer_template = template.render(divisioninfo=divisioninfo,
                                                assessmentinfo=assessmentinfo,
                                                info=info,
                                                percent_scores=percent_scores,
                                                sendto=self.sendto["division"][sendto])

            output_file = self.division_out_file_prefix + "_" + str(divisionid) + "_" + sendto
            with open(output_file + ".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)

            os.system("xelatex -output-directory {} {}".format(
                os.path.realpath(self.build_d),
                os.path.realpath(output_file)))
            shutil.copy2(self.build_d + "/" + output_file + ".pdf", outputdir)
            self.deleteTempFiles([output_file + ".tex",
                                  self.build_d + "/" + output_file + ".pdf"])
        return outputdir



    def getYearMonth(self, inputdate):
        print(inputdate)
        year = int(inputdate[0:4])
        month = self.translatedmonth[self.language][int(inputdate[5:7])]
        return year, month

    def handle(self, *args, **options):
        divisionids = options.get("divisionid", None)
        if divisionids is not None:
            self.divisionids = [int(x) for x in divisionids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)
        self.language = options.get("lang")
        self.templatedir = self.templatedir + "/" + self.language + "/"
        self.imagesdir = self.imagesdir + "/" + self.language + "/"

        reportcolour = options.get("reportcolour")
        self.imagesdir = self.imagesdir + "/" + reportcolour + "/"

        print(self.imagesdir)

        if not self.validateInputs():
            return
        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        self.createDivisionReports()

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
