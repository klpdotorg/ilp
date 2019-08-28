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


class Command(BaseCommand):
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
    schooloutputdir = "schoolreports"
    school_out_file_prefix = "HouseHoldSchoolReport"

    schoolsummary = []
    # gp_template_name = "GPReport.tex"
    # school_template_name = "GPSchoolReport.tex"
    # gp_template_file = basefiledir+templatedir+gp_template_name
    # school_template_file = basefiledir+templatedir+school_template_name

    templates = {"school": {"template": "HouseHold.tex", "latex": None}}

    build_d = basefiledir+"/build/"
    gpids = None
    survey = None
    surveyid = None
    schoolids = None
    districtids = None
    colour = "bw"
    imagesdir = basefiledir+"/apps/gpcontest/images/"

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--sid', nargs='?')
        parser.add_argument('--districtid', nargs='?')
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
        if self.gpids is not None:
            for gp in self.gpids:
                try:
                    self.gp[gp] = ElectionBoundary.objects.get(
                            id=gp, const_ward_type='GP')
                except ElectionBoundary.DoesNotExist:
                    print("Invalid gpid: "+str(gp)+" passed")
                    return False

        if self.districtids is not None:
            for districtid in self.districtids:
                try:
                   Boundary.objects.get(
                            id=districtid, boundary_type_id='SD')
                except Boundary.DoesNotExist:
                    print("Invalid districtid: "+str(districtid)+" passed")
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

    
    def createSchoolHouseHoldReports(self):
        schooldata = household_report.get_hh_reports_for_school_ids(self.surveyid,
                                                   self.schoolids,
                                                   self.startyearmonth, 
                                                   self.endyearmonth)

        print(schooldata)
        self.createSchoolPdfs(schooldata)

    def createHouseHoldReportBoundary(self):
        schooldata = household_report.get_hh_reports_for_districts(self.surveyid,
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
                          "month": self.getYearMonth(self.startyearmonth)+"-"+self.getYearMonth(self.endyearmonth)}
            assessmentinfo = schooldata["answers"]
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
                    info=info, schoolinfo=schoolinfo, survey=survey)
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

    def deleteTempFiles(self, tempFiles):
        for f in tempFiles:
            os.remove(f)

    def mergeReports(self, outputdir, gpfile, schoolfiles, outputfile):
        inputfiles = [outputdir+gpfile]
        for schoolfile in schoolfiles:
            inputfiles.append(outputdir+schoolfile)
        self.combinePdfs(inputfiles, outputfile, outputdir) 
        self.deleteTempFiles(inputfiles)

    def combinePdfs(self, inputfiles, outputfile, outputdir):
        input_streams = []
        try:
            # First open all the files, then produce the output file, and
            # finally close the input files. This is necessary because
            # the data isn't read from the input files until the write
            # operation.
            output_stream = open(outputdir+"/"+outputfile, 'wb')
            for input_file in inputfiles:
                input_streams.append(open(input_file, 'rb'))
                writer = PdfFileWriter()
                for reader in map(PdfFileReader, input_streams):
                    for n in range(reader.getNumPages()):
                        writer.addPage(reader.getPage(n))
                writer.write(output_stream)
        finally:
            for f in input_streams:
                f.close()

    def getAcademicYear(self, startyearmonth, endyearmonth):
        startyear = int(startyearmonth[0:4])
        startmonth = int(startyearmonth[4:6])
        if startmonth <= 5:
            acadyear = str(startyear-1)+"-"+str(startyear)
        else:
            acadyear = str(startyear)+"-"+str(startyear+1)
        return acadyear

    def handle(self, *args, **options):
        gpids = options.get("gpid", None)
        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
        self.surveyid = options.get("surveyid", None)
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

        os.system('tar -cvf '+self.outputdir+'.tar '+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
