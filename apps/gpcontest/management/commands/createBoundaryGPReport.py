import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import Boundary
from gpcontest.reports import generate_report, school_compute_numbers, generate_boundary_reports


class Command(BaseCommand):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates Distrct and Block Reports, pass surveyid startyearmonth endyearmonth\
            --districtid [commaseparated districtids] --onlydistrict (True/False) \
            --blocksblockid [comma separated blockids]'
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
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

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--districtid', nargs='?')
        parser.add_argument('--onlydistrict', nargs='?')
        parser.add_argument('--blockid', nargs='?')
        parser.add_argument('--reportcolour', nargs='?', default='bw')

    def initiatelatex(self):
        # create the build directory if not existing
        if not os.path.exists(self.build_d):
            os.makedirs(self.build_d)
        latex_jinja_env = jinja2.Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_comment_prefix='%%',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(os.path.abspath('/'))
        )
        for filetype in self.templates:
            self.templates[filetype]["latex"] = latex_jinja_env.get_template(
                self.basefiledir+self.templatedir+self.templates[filetype]["template"])

    def checkYearMonth(self, yearmonth):
        try:
            datetime.strptime(yearmonth, '%Y%m')
        except ValueError:
            return False
        return True

    def validateInputs(self):
        if self.districtids is not None:
            for district in self.districtids:
                try:
                    self.district[district] = Boundary.objects.get(
                            id=district, boundary_type='SD')
                except Boundary.DoesNotExist:
                    print("Invalid district id: "+str(district)+" passed")
                    return False
       
        if self.blockids is not None:
            for block in self.blockids:
                try:
                    block = Boundary.objects.get(
                            id=block, boundary_type='SB')
                except Boundary.DoesNotExist:
                    print("Invalid block id: "+str(block)+" passed")
                    return False
        try:
            self.survey = Survey.objects.get(id=self.surveyid)
        except Survey.DoesNotExist:
            print("Invalid surveyid: "+str(self.surveyid)+" passed")
            return False

        if not self.checkYearMonth(self.startyearmonth):
            print("Start year month format is invalid it should be YYYYMM, " +
                  self.startyearmonth)
            return False

        if not self.checkYearMonth(self.endyearmonth):
            print("End year month format is invalid it should be YYYYMM, " +
                  self.endyearmonth)
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
            #print(data["district_info"][district])
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
        #print(districtdata, file=self.utf8stdout)
        template = self.templates["district"]["latex"]
        if type(districtdata) is int or type(districtdata) is str:
            return
        districtinfo = {"name": districtdata["boundary_name"].capitalize(),
                  "num_blocks": districtdata["num_blocks"],
                  "num_gps": districtdata["num_gps"],
                  "num_schools": districtdata["num_schools"],
                  "totalstudents": districtdata["num_students"]}
        assessmentinfo = []
        for assessment in self.assessmentnames:
            if self.assessmentnames[assessment]["name"] in districtdata:
                districtdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(districtdata[self.assessmentnames[assessment]["name"]])
        # print(assessmentinfo)
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        if "percent_scores" not in districtdata:
            percent_scores = None
        else:
            percent_scores = districtdata["percent_scores"]
        renderer_template = template.render(districtinfo=districtinfo,
                                            assessmentinfo=assessmentinfo,
                                            info=info,
                                            percent_scores=percent_scores)

        output_file = self.district_out_file_prefix+"_"+str(districtid)
        if onlyDistrict:
            outputdir = self.outputdir+"/districts"
        else:
            outputdir = self.outputdir+"/"+str(districtid)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

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
        #print(blockdata, file=self.utf8stdout)
        template = self.templates["block"]["latex"]
        blockinfo = {"name": blockdata["boundary_name"].capitalize(),
                  "districtname": blockdata["parent_boundary_name"].capitalize(),
                  "num_gps": blockdata["num_gps"],
                  "school_count": blockdata["num_schools"],
                  "totalstudents": blockdata["num_students"]}
        assessmentinfo = []
        for assessment in self.assessmentnames:
            if self.assessmentnames[assessment]["name"] in blockdata:
                blockdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(blockdata[self.assessmentnames[assessment]["name"]])
        # print(assessmentinfo)
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        if "percent_scores" not in blockdata:
            percent_scores = None
        else:
            percent_scores = blockdata["percent_scores"]
        renderer_template = template.render(blockinfo=blockinfo,
                                            assessmentinfo=assessmentinfo,
                                            info=info,
                                            percent_scores=percent_scores)

        output_file = self.block_out_file_prefix+"_"+str(blockid)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

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



    def deleteTempFiles(self, tempfiles):
        for filename in tempfiles:
            os.remove(filename)


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


    def getAcademicYear(self, startyearmonth, endyearmonth):
        startyear = int(startyearmonth[0:4])
        startmonth = int(startyearmonth[4:6])
        if startmonth <= 5:
            acadyear = str(startyear-1)+"-"+str(startyear)
        else:
            acadyear = str(startyear)+"-"+str(startyear+1)
        return acadyear

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
