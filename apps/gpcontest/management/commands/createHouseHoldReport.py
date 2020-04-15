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
    gp_out_file_prefix = "GPHouseHoldReport"
    templates = {"school": {"template": "SchoolHouseHold.tex", "latex": None},
                 "gp": {"template": "GPHouseHold.tex", "latex": None}}
    build_d = basefiledir+"/build/"
    gpids = None
    survey = None
    surveyid = None
    gpsurveyid = None
    schoolids = None
    districtids = None
    colour = "bw"
    imagesdir = basefiledir+"/apps/gpcontest/images/english/"
    validqids = {138,144,145,269,147,148,149,150}
    months = ["Jan","Feb","March","April","May","June","July","Aug","Sept","Oct","Nov"]
    data = {}

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

        self.createSchoolPdfs(schooldata)


    def createHouseHoldReportBoundary(self):
        schooldata = household_report.get_hh_reports_for_districts(self.surveyid,
                                                   self.gpsurveyid,
                                                   self.districtids,
                                                   self.startyearmonth, 
                                                   self.endyearmonth)

        self.createSchoolPdfs(schooldata)


    def getYearMonth(self, yearmonth):
        return self.months[int(yearmonth[4:6])-1]+"/"+yearmonth[0:4]


    def createGPLetter(self, schooldata, schoolinfo, info, outputdir):
        gpinfo = {}
        gpinfo["gp_langname"] = schoolinfo["gp_langname"]
        gpinfo["gpname"] = schoolinfo["gpname"]
        gpinfo["gpid"] = schooldata["gp_id"]
        gpinfo["district_langname"] = schoolinfo["district_langname"]
        gpinfo["districtname"] = schoolinfo["district"]
        gpinfo["block_langname"] = schoolinfo["block_langname"]
        gpinfo["blockname"] = schoolinfo["block"]
        gpinfo["numassessments"] = schooldata['gp_info']['total_assessments']
        gpinfo["compare"] = {"parent": {"addition": schooldata['gp_info']['parents_perception']['Addition'],
                                        "subtraction": schooldata['gp_info']['parents_perception']['Subtraction']},
                             "gpcontest":{"addition": schooldata['gp_info']['gpcontest_data']['Addition'],
                                          "subtraction": schooldata['gp_info']['gpcontest_data']['Subtraction']}}
 
        renderer_template = self.templates["gp"]["latex"].render(
                    info=info, gpinfo=gpinfo)
        gp_out_file = self.gp_out_file_prefix+"_" +str(gpinfo["gpid"])
        with open(gp_out_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)
        os.system("xelatex -output-directory {} {}".format(
            os.path.realpath(self.build_d),
            os.path.realpath(gp_out_file)))
        shutil.copy2(self.build_d+"/"+gp_out_file+".pdf", outputdir)
        self.deleteTempFiles([gp_out_file+".tex"])
        self.deleteTempFiles([self.build_d+"/" + gp_out_file+".pdf"])
        return gp_out_file+".pdf"


    def createSchoolPdfs(self, schoolsdata):
        info = {"imagesdir": self.imagesdir, "year": self.academicyear, "date": self.now.strftime("%d/%m/%Y")}
        for schoolid in schoolsdata:
            schooldata = schoolsdata[schoolid]
            print("School Data is:")
            print(schooldata, file=self.utf8stdout)

            gpid = schooldata["gp_id"]
            districtid = schooldata["district_id"]
            blockid = schooldata["block_id"]
            if districtid not in self.data:
                self.data[districtid] = {"blocks":{}, "name":schooldata["district_name"]}
                self.data[districtid]["blocks"][blockid] = {"name":schooldata["block_name"], "gps":{}}
                self.data[districtid]["blocks"][blockid]["gps"][gpid] = {"name":schooldata["gp_name"],"pdf":"","schoolpdfs":[]}
                creategpletter = True
            elif blockid not in self.data[districtid]["blocks"]:
                self.data[districtid]["blocks"][blockid] = {"name":schooldata["block_name"], "gps":{}}
                self.data[districtid]["blocks"][blockid]["gps"][gpid] = {"name":schooldata["gp_name"],"pdf":"","schoolpdfs":[]}
                creategpletter = True
            elif gpid not in self.data[districtid]["blocks"][blockid]["gps"]:
                self.data[districtid]["blocks"][blockid]["gps"][gpid] = {"name":schooldata["gp_name"],"pdf":"","schoolpdfs":[]}
                creategpletter = True

            print(self.data[districtid]["blocks"][blockid]["gps"][gpid]["schoolpdfs"])

            if schooldata["district_langname"] == "":
                districtname = schooldata["district_name"].capitalize()
            else:
                districtname = "("+schooldata["district_name"].capitalize()+")"
            if schooldata["block_langname"] == "":
                blockname = schooldata["block_name"].capitalize()
            else:
                blockname = "("+schooldata["block_name"].capitalize()+")"
            if schooldata["gp_langname"] == "":
                gpname = schooldata["gp_name"].capitalize()
            else:
                gpname = "("+schooldata["gp_name"].capitalize()+")"
            schoolinfo = {"district": districtname,
                          "district_langname": schooldata["district_langname"],
                          "block": blockname,
                          "block_langname": schooldata["block_langname"],
                          "schoolname": schooldata["school_name"].capitalize(),
                          "village": schooldata["village_name"].capitalize(),
                          "klpid": schoolid,
                          "disecode": schooldata["dise_code"],
                          "gpid": schooldata["gp_id"],
                          "gpname": gpname,
                          "gp_langname": schooldata["gp_langname"],
                          "numparentassessments": schooldata["total_parental_assessments"],
                          "numassessments": schooldata["total_assessments"],
                          "month": self.getYearMonth(self.startyearmonth)+"-"+self.getYearMonth(self.endyearmonth)}
            compare = {"parent":schooldata["parents_perception"], "gpcontest": schooldata["gpcontest_data"]}
            assessmentinfo = []
            for question in schooldata["answers"]:
                if question["question_id"] in self.validqids:
                    assessmentinfo.append(question)

            outputdir = self.outputdir+"/"+schooldata["district_name"]+"/"+schooldata["block_name"]+"/"#+schooldata["gp_name"]+"/"
            if not os.path.exists(outputdir):
                os.makedirs(outputdir)
            if not os.path.exists(self.build_d):
                os.makedirs(self.build_d)

            if creategpletter:
                gppdf = self.createGPLetter(schooldata, schoolinfo, info, outputdir)
                self.data[districtid]["blocks"][blockid]["gps"][gpid]["pdf"] = gppdf 
                self.data[districtid]["blocks"][blockid]["gps"][gpid]["outputpath"] = outputdir 

            temppdfscreated = []
            survey = {}
            survey["assessmentinfo"] = assessmentinfo
            renderer_template = self.templates["school"]["latex"].render(
                    info=info, schoolinfo=schoolinfo,compare=compare, survey=survey)
            school_out_file = self.school_out_file_prefix+"_" +\
                                    str(schoolinfo["klpid"])
            with open(school_out_file+".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)
            os.system("xelatex -output-directory {} {}".format(
                os.path.realpath(self.build_d),
                os.path.realpath(school_out_file)))
            shutil.copy2(self.build_d+"/"+school_out_file+".pdf", outputdir)
            temppdfscreated.append(os.path.realpath(self.build_d+"/" +
                                   school_out_file+".pdf"))
            self.data[districtid]["blocks"][blockid]["gps"][gpid]["schoolpdfs"].append(school_out_file+".pdf")
            self.deleteTempFiles([school_out_file+".tex"])

        self.deleteTempFiles(temppdfscreated)
        return 


    def mergeFiles(self):
        for districtid in self.data:
            for blockid in self.data[districtid]["blocks"]:
                for gpid in self.data[districtid]["blocks"][blockid]["gps"]:
                    gppdf = self.data[districtid]["blocks"][blockid]["gps"][gpid]["pdf"]
                    schoolpdfs = self.data[districtid]["blocks"][blockid]["gps"][gpid]["schoolpdfs"]
                    combinedFile =  "HouseHoldReport_"+str(gpid)+".pdf"
                    outputdir = self.data[districtid]["blocks"][blockid]["gps"][gpid]["outputpath"]
                    self.mergeReports(outputdir+"/", gppdf, schoolpdfs, combinedFile)


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

        reportcolour = options.get("reportcolour")
        self.imagesdir = self.imagesdir+"/"+reportcolour+"/"

        if schoolids is not None:
            self.schoolids = [int(x) for x in schoolids.split(',')]

        districtids = options.get("districtid", None)
        if districtids is not None:
            self.districtids = [int(x) for x in districtids.split(',')]

        if not self.validateInputs():
            return
        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        if self.schoolids is not None:
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

        self.mergeFiles()

        os.system('tar -cvf '+self.outputdir+'.tar '+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
