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
    help = 'Creates Distrct and Block Reports, pass surveyid startyearmonth endyearmonth\
            --districtid [commaseparated districtids] --onlydistrict (True/False) \
            --blocksblockid [comma separated blockids]'
    assessmentorder = ["class4", "class5", "class6"]
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
    sendto = {"block": {
        "executiveofficer":{"langname":"ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು", "name":"Executive Officer"},
        "blockeducationofficer":{"langname":"ಕ್ಷೇತ್ರ ಶಿಕ್ಷಣಾಧಿಕಾರಿಗಳು", "name": "Block Education Officer"},
        "mla":{"langname":" ಮಾನ್ಯ ಶಾಸಕರು","name":"Honorable MLA"},
        "president":{"langname":"ತಾಲೂಕು ಪಂಚಾಯತಿ ಅಧ್ಯಕ್ಷರು","name":"Taluk Panchayath President"},
        "brc":{"langname":"ಕ್ಷೇತ್ರ ಸಮನ್ವಯಾಧಿಕಾರಿಗಳು","name":"Block Resource Centers"} },
        "district": {
            "deputycommissioner":{"langname":"ಜಿಲ್ಲಾದಿಕಾರಿಗಳು","name":"The Deputy Commissioner"},
            "ceo":{"langname":"ಮುಖ್ಯ ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು","name":"Chief Executive Officer"},
            "president":{"langname":"ಜಿಲ್ಲಾ ಪಂಚಾಯತ್ ಅಧ್ಯಕ್ಷರು", "name":"Zilla Panchayath President"},
            "ddpi":{"langname":"ಉಪ ನಿರ್ದೇಶಕರು", "name":"DDPI"},
            "mp":{"langname":"ಮಾನ್ಯ ಸಂಸದರು","name":"Honorable MP"}}}
    now = date.today()
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir+"/generated_files/gpreports/"+str(now)+"/BoundaryReports/"
    districtoutputdir = "districtreports"
    blockoutputdir = "blockreports"
    district_out_file_prefix = "DistrictGPReport"
    block_out_file_prefix = "BlockGPReport"

    districtsummary = []
    blocksummary = []

    templates = {"block": {"template": "BlockGPReport.tex", "latex": None},
                 "district": {"template": "DistrictGPReport.tex", "latex": None},
                 "districtsummary": {"template": "DistrictGPSummary.tex",
                               "latex": None},
                 "blocksummary": {"template": "BlockGPSummary.tex",
                                   "latex": None}}

    build_d = basefiledir+"/build/"
    district = {}
    survey = None
    districtids = None
    surveyid = None
    onlydistrict = False
    block = {}
    blockids = None
    colour = "bw"
    imagesdir = basefiledir+"/apps/gpcontest/images/"
    translatedmonth = {1:'ಜನವರಿ',2:'ಫೆಬ್ರವರಿ',3:'ಮಾರ್ಚ್',4:'ಎಪ್ರಿಲ್',5:'ಮೇ',6:'ಜೂನ್',7:'ಜುಲೈ',8:'ಆಗಸ್ಟ್',9:'ಸೆಪ್ಟಂಬರ್',10:'ಅಕ್ಟೋಬರ್',11:'ನವೆಂಬರ್',12:'ಡಿಸೆಂಬರ್'}
    language = 'kannada'

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--districtid', nargs='?')
        parser.add_argument('--onlydistrict', nargs='?')
        parser.add_argument('--blockid', nargs='?')
        parser.add_argument('--reportcolour', nargs='?', default='bw')
        parser.add_argument('--lang', nargs='?', default='kannada')

    def validateInputs(self):
        if self.districtids is not None:
            if not self.validateBoundaryIds(self.districtids, 'SD'):
                return False
       
        if self.blockids is not None:
            if not self.validateBoundaryIds(self.blockids, 'SB'):
                return False
        if not self.validateSurveyId(self.surveyid):
            return False

        if not self.checkYearMonth(self.startyearmonth):
            return False
        if not self.checkYearMonth(self.endyearmonth):
            return False
        return True

    def createDistrictReports(self):
        data = {}
        if self.onlydistrict:
            childReports = False
        else:
            childReports = True
        if self.districtids is None:
            data = generate_boundary_reports.generate_all_district_reports(self.surveyid,
                                                        self.startyearmonth,
                                                        self.endyearmonth, childReports)
        else:
            data["district_info"] = {}
            data["district_info"] = generate_boundary_reports.generate_boundary_reports(
                        self.surveyid, self.districtids, self.startyearmonth,
                        self.endyearmonth, childReports)

        for district in data["district_info"]:
            outputdir = self.createDistrictPdfs(district,
                                                data["district_info"][district], self.onlydistrict
                                                )
            if not self.onlydistrict:
                for block in data["district_info"][district]["blocks"]:
                    self.createBlockPdfs(block, data["district_info"][district]["blocks"][block], outputdir, self.build_d)
                self.createBlockSummarySheet(outputdir)

        self.createDistrictSummarySheet()

    def createDistrictSummarySheet(self):
        info = {"date": self.now, "num_districts": len(self.districtsummary)}
        renderer_template = self.templates["districtsummary"]["latex"].render(
                                                districts=self.districtsummary, info=info)

        # saves tex_code to outpout file
        outputfile = "DistrictGPSummary"
        with open(outputfile+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(outputfile)))
        shutil.copy2(self.build_d+"/"+outputfile+".pdf", self.outputdir)
        self.deleteTempFiles([outputfile+".tex",
                             self.build_d+"/"+outputfile+".pdf"])

    def createDistrictPdfs(self, districtid, districtdata, onlyDistrict):
        template = self.templates["district"]["latex"]
        if type(districtdata) is int or type(districtdata) is str:
            return

        if districtdata["boundary_langname"] == "":
            districtname = districtdata["boundary_name"].capitalize()
        else:
            districtname = "("+districtdata["boundary_name"].capitalize()+")"
 
        districtinfo = {"name": districtname,
                  "langname": districtdata["boundary_langname"],
                  "num_blocks": districtdata["num_blocks"],
                  "num_gps": districtdata["num_gps"],
                  "num_schools": districtdata["num_schools"],
                  "totalstudents": districtdata["num_students"]}

        assessmentinfo = []
        for assessment in self.assessmentorder:
            if self.assessmentnames[assessment]["name"] in districtdata:
                districtdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(districtdata[self.assessmentnames[assessment]["name"]])
        year, month = self.getYearMonth(str(self.now))
        info = {"imagesdir": self.imagesdir, "acadyear": self.academicyear, "year":year, "month": month}
        print("info month",info)
        percent_scores = {}
        if "percent_scores" not in districtdata:
            percent_scores = None
        else:
            for assessment in districtdata["percent_scores"]:
                numcompetency = 0
                for competency in districtdata["percent_scores"][assessment]:
                    if districtdata["percent_scores"][assessment][competency] == 'NA':
                        continue
                    numcompetency += 1
                    if percent_scores == {}:
                        percent_scores["assessments"] = {}
                    if assessment in percent_scores["assessments"]:
                        percent_scores["assessments"][assessment][competency] = districtdata["percent_scores"][assessment][competency]
                    else:
                        percent_scores["assessments"][assessment] = {competency: districtdata["percent_scores"][assessment][competency]}
            percent_scores["num_competencies"] = numcompetency


        if onlyDistrict:
            outputdir = self.outputdir+"/districts"
        else:
            outputdir = self.outputdir+"/districts/"+str(districtid)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        for sendto in self.sendto["district"]:
            renderer_template = template.render(districtinfo=districtinfo,
                                                assessmentinfo=assessmentinfo,
                                                info=info,
                                                percent_scores=percent_scores,
                                                sendto=self.sendto["district"][sendto])

            output_file = self.district_out_file_prefix+"_"+str(districtid)+"_"+sendto
            with open(output_file+".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)

            os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(output_file)))
            shutil.copy2(self.build_d+"/"+output_file+".pdf", outputdir)
            self.deleteTempFiles([output_file+".tex",
                             self.build_d+"/"+output_file+".pdf"])

        self.districtsummary.append({"districtid": districtid,
                               "districtname": districtdata["boundary_name"].capitalize(),
                               "num_schools": districtdata["num_schools"],
                               "num_blocks": districtdata["num_blocks"],
                               "num_students": districtdata["num_students"]})
        return outputdir


    def createBlockPdfs(self, blockid, blockdata, outputdir, build_dir):
        template = self.templates["block"]["latex"]

        if blockdata["parent_langname"] == "":
           districtname = blockdata["parent_boundary_name"].capitalize()
        else:
            districtname = "("+blockdata["parent_boundary_name"].capitalize()+")"

        if blockdata["boundary_langname"] == "":
            blockname = blockdata["boundary_name"].capitalize()
        else:
            blockname = "("+blockdata["boundary_name"].capitalize()+")"
 
        blockinfo = {"blockname": blockname,
                  "block_langname": blockdata["boundary_langname"],
                  "districtname": districtname,
                  "district_langname": blockdata["parent_langname"],
                  "num_gps": blockdata["num_gps"],
                  "school_count": blockdata["num_schools"],
                  "totalstudents": blockdata["num_students"]}
        assessmentinfo = []
        for assessment in self.assessmentorder:
            if self.assessmentnames[assessment]["name"] in blockdata:
                blockdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(blockdata[self.assessmentnames[assessment]["name"]])
        year, month = self.getYearMonth(str(self.now))
        info = {"imagesdir": self.imagesdir, "acadyear": self.academicyear, "year":year, "month": month}
        percent_scores = {}
        if "percent_scores" not in blockdata:
            percent_scores = None
        else:
            for assessment in blockdata["percent_scores"]:
                numcompetency = 0
                for competency in blockdata["percent_scores"][assessment]:
                    if blockdata["percent_scores"][assessment][competency] == 'NA':
                        continue
                    numcompetency += 1
                    if percent_scores == {}:
                        percent_scores["assessments"] = {}
                    if assessment in percent_scores["assessments"]:
                        percent_scores["assessments"][assessment][competency] = blockdata["percent_scores"][assessment][competency]
                    else:
                        percent_scores["assessments"][assessment] = {competency: blockdata["percent_scores"][assessment][competency]}
            percent_scores["num_competencies"] = numcompetency

        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        for sendto in self.sendto["block"]:

            renderer_template = template.render(blockinfo=blockinfo,
                                            assessmentinfo=assessmentinfo,
                                            info=info,
                                            percent_scores=percent_scores,
                                            sendto=self.sendto["block"][sendto])


            output_file = self.block_out_file_prefix+"_"+str(blockid)+"_"+sendto

            with open(output_file+".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)

            os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(build_dir),
                      os.path.realpath(output_file)))
            shutil.copy2(build_dir+"/"+output_file+".pdf", outputdir)
            self.deleteTempFiles([output_file+".tex",
                             build_dir+"/"+output_file+".pdf"])

        self.blocksummary.append({"blockid": blockid,
                               "blockname": blockdata["boundary_name"].capitalize(),
                               "num_schools": blockdata["num_schools"],
                               "num_students": blockdata["num_students"]})
        return outputdir


    def getYearMonth(self, inputdate):
        print(inputdate)
        year = int(inputdate[0:4])
        month = self.translatedmonth[int(inputdate[5:7])]
        return year, month
        

    def createBlockReports(self):
        block_outputdir = self.outputdir+"/blocks/"
        blockinfo = generate_boundary_reports.generate_boundary_reports(
                        self.surveyid, self.blockids, self.startyearmonth,
                        self.endyearmonth)

        for block in blockinfo:
            block_builddir = self.build_d+str(self.now) + \
                              "/blocks/"+str(block)
            self.createBlockPdfs(block, blockinfo[block], block_outputdir,
                                      block_builddir)
        self.createBlockSummarySheet(block_outputdir)


    def createBlockSummarySheet(self, outputdir):
        info = {"date": self.now, "num_blocks": len(self.blocksummary)}
        renderer_template = self.templates["blocksummary"]["latex"].render(
                                                blocks=self.blocksummary, info=info)

        # saves tex_code to outpout file
        outputfile = "BlockGPSummary"
        with open(outputfile+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(outputfile)))
        shutil.copy2(self.build_d+"/"+outputfile+".pdf", outputdir)
        self.deleteTempFiles([outputfile+".tex",
                             self.build_d+"/"+outputfile+".pdf"])


    def handle(self, *args, **options):
        districtids = options.get("districtid", None)
        if districtids is not None:
            self.districtids = [int(x) for x in districtids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)
        self.onlydistrict = options.get("onlydistrict", False)
        blockids = options.get("blockid", None)

        self.language = options.get("lang")
        self.templatedir = self.templatedir+"/"+self.language+"/"
        self.imagesdir = self.imagesdir+"/"+self.language+"/"

        reportcolour = options.get("reportcolour")
        self.imagesdir = self.imagesdir+"/"+reportcolour+"/"

        if blockids is not None:
            self.blockids = [int(x) for x in blockids.split(',')]

        if not self.validateInputs():
            return
        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        if self.blockids is not None:
            self.createBlockReports()
        else:
            self.createDistrictReports()

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
