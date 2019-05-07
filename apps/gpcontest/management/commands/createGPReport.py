import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import ElectionBoundary
from gpcontest.reports import generate_report, school_compute_numbers

class Command(BaseCommand):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates GP and School Reports, pass --gpid [commaseparated gpids]\
            surveyid startyearmonth endyearmonth--onlygp (True/False) \
            --sid [comma separated schoolids]'
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
    now = date.today()
    basefiledir = os.getcwd()+"/apps/gpcontest/"
    relpath_schools = "apps/gpcontest/pdfs/"+str(now)+"/schools/"
    templatedir = "templates/"
    outputdir = basefiledir+"pdfs/"+str(now)
    gpoutputdir = "gpreports"
    schooloutputdir = "schoolreports"
    gp_out_file_prefix = "GPReport"
    school_out_file_prefix = "SchoolReport"

    gpsummary = []
    schoolsummary = []
    # gp_template_name = "GPReport.tex"
    # school_template_name = "GPSchoolReport.tex"
    # gp_template_file = basefiledir+templatedir+gp_template_name
    # school_template_file = basefiledir+templatedir+school_template_name

    templates = {"school": {"template": "GPSchoolReport.tex", "latex":None},
                 "gp": {"template": "GPReport.tex", "latex": None},
                 "gpsummary": {"template": "GPReportGPSummary.tex", "latex": None},
                 "schoolsummary": {"template": "GPReportSchoolSummary.tex", "latex": None}
                }

    build_d = basefiledir+"/build/"
    gp = {}
    survey = None
    gpids = None
    surveyid = None
    onlygp = False
    schoolids = None
    imagesdir = basefiledir+"images/"

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--gpid', nargs='?')
        parser.add_argument('--onlygp', nargs='?')
        parser.add_argument('--sid', nargs='?')

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

    def createGPReports(self):
        data = {}
        if self.gpids is None:
            data = generate_report.generate_all_reports(self.surveyid,
                                                        self.startyearmonth,
                                                        self.endyearmonth)
        else:
            for gp in self.gpids:
                data[gp] = generate_report.generate_gp_summary(
                        gp, self.surveyid, self.startyearmonth,
                        self.endyearmonth)

        gpinfo = []
        print("All GPs data is")
        print(data, file=self.utf8stdout)
        for gp in data["gp_info"]:
            print(gp)
            outputdir = self.createGPPdfs(gp, data["gp_info"][gp], self.templates["gp"]["latex"])
                          
            if not self.onlygp:
                print(gp)
                self.createSchoolReports(gp, outputdir)
        self.createGPSummarySheet()

    def createGPSummarySheet(self):
        info = {"date": self.now}
        renderer_template = self.templates["gpsummary"]["latex"].render(gps=self.gpsummary, info=info)

        # saves tex_code to outpout file
        outputfile = "GPContestGPSummary"
        with open(outputfile+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(outputfile)))
        shutil.copy2(self.build_d+"/"+outputfile+".pdf", self.outputdir)
        self.deleteTempFiles([outputfile+".tex",
                             self.build_d+"/"+outputfile+".pdf"])
        
 
    def createGPPdfs(self, gpid, gpdata, template):
        print("IN CREATE PDFS")
        print(gpdata, file=self.utf8stdout)
        if type(gpdata) is int or type(gpdata) is str:
            return
        gpdata["contestdate"] = ', '.join(gpdata["date"])
        gpinfo = {"gpname": gpdata["gp_name"].capitalize(),
                  "block": gpdata["block"].capitalize(),
                  "district": gpdata["district"].capitalize(),
                  "cluster": gpdata["cluster"].capitalize(),
                  "contestdate": gpdata["contestdate"],
                  "school_count": gpdata["num_schools"],
                  "totalstudents": gpdata["num_students"]}
        assessmentinfo = {}
        for assessment in self.assessmentnames:
            assessmentinfo[assessment] = gpdata[self.assessmentnames[assessment]["name"]]
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        renderer_template = template.render(gpinfo=gpinfo,
                                            assessmentinfo = assessmentinfo,
                                            info=info)

        output_file = self.gp_out_file_prefix+"_"+str(gpid)
        outputdir = self.outputdir+"/"+str(gpid)
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

        self.gpsummary.append({"gpid": gpid,
                               "gpname": gpdata["gp_name"].capitalize(),
                               "total_schools": gpdata["num_schools"],
                               "class4_schools": gpdata["class4_num_schools"],
                               "class5_schools": gpdata["class5_num_schools"],
                               "class6_schools": gpdata["class6_num_schools"]})
        return outputdir

    def createOnlySchoolReports(self):
        school_outputdir = self.outputdir+"/schools/"
        for school in self.schoolids:
            schooldata = school_compute_numbers.get_school_report(
                                       school, self.surveyid,
                                       self.startyearmonth, self.endyearmonth)
            school_builddir = self.build_d+str(self.now) + \
                              "/schools/"+str(schooldata["school_id"])
            self.createSchoolPdfs(schooldata, school_builddir,
                                  school_outputdir)
        self.createSchoolsSummary(school_outputdir)

    def createSchoolPdfs(self, schooldata, builddir, outputdir):
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        contestdate = ', '.join(schooldata["date"])
        #print(schooldata, file=self.utf8stdout)
        schoolinfo = {"district": schooldata["district_name"].capitalize(),
                      "block": schooldata["block_name"].capitalize(),
                      "gpname": schooldata["gp_name"].capitalize(),
                      "schoolname": schooldata["school_name"].capitalize(),
                      "klpid": schooldata["school_id"],
                      "gpid": schooldata["gp_id"],
                      "disecode": schooldata["dise_code"],
                      "contestdate": contestdate}
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        if not os.path.exists(builddir):
            os.makedirs(builddir)

        pdfscreated = []
        summary = {"gpid": schooldata["gp_id"],
                   "gpname": schooldata["gp_name"],
                   "schoolname": schooldata["school_name"],
                   "dise_code": schooldata["dise_code"],
                   "generated": self.now,
                   "assessmentcounts": {}}
        for assessment in self.assessmentnames:
            summary["assessmentcounts"][self.assessmentnames[assessment]["class"]] = 0
            if self.assessmentnames[assessment]["name"] in schooldata:
                info["classname"] = self.assessmentnames[assessment]["class"]
                assessmentinfo = schooldata[self.assessmentnames[assessment]["name"]]
                summary["assessmentcounts"][self.assessmentnames[assessment]["class"]] = schooldata[self.assessmentnames[assessment]["name"]]["num_students"]
                #print(assessmentinfo, file=self.utf8stdout)
                renderer_template = self.templates["school"]["latex"].render(
                    info=info, schoolinfo=schoolinfo,
                    assessmentinfo=assessmentinfo)
                school_out_file = self.school_out_file_prefix+"_" +\
                                    str(schoolinfo["klpid"])+"_"+str(self.assessmentnames[assessment]["class"])
                with open(school_out_file+".tex", "w", encoding='utf-8') as f:
                    f.write(renderer_template)
                os.system("xelatex -output-directory {} {}".format(
                os.path.realpath(builddir),
                os.path.realpath(school_out_file)))
                pdfscreated.append(os.path.realpath(builddir+"/" +
                               school_out_file+".pdf"))
                self.deleteTempFiles([school_out_file+".tex"])


        school_file = self.school_out_file_prefix+"_"+str(schoolinfo["klpid"])+".pdf"
        self.combinePdfs(pdfscreated, school_file, outputdir)
        self.deleteTempFiles(pdfscreated)
        self.schoolsummary.append(summary)


    def deleteTempFiles(self, tempPdfs):
        for pdf in tempPdfs:
            os.remove(pdf)

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

    def createSchoolReports(self, gpid, outputdir):
        schoolsdata = school_compute_numbers.get_gp_schools_report(
                gpid, self.surveyid, self.startyearmonth, self.endyearmonth)

        for schoolid in schoolsdata:
            schooldata = schoolsdata[schoolid]
            school_builddir = self.build_d+str(self.now)+"/"+str(gpid)+"/" +\
                    str(schooldata["school_id"])
            self.createSchoolPdfs(schooldata, school_builddir, outputdir)
        self.createSchoolsSummary(outputdir)

    def createSchoolsSummary(self, outputdir):
        # print(self.schoolsummary)
        info = {"date": self.now}
        renderer_template = self.templates["schoolsummary"]["latex"].render(schools=self.schoolsummary, info=info)

        # saves tex_code to outpout file
        outputfile = "GPContestSchoolSummary"
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
        gpids = options.get("gpid", None)
        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)
        self.onlygp = options.get("onlygp", False)
        schoolids = options.get("sid", None)
        if schoolids is not None:
            self.schoolids = [int(x) for x in schoolids.split(',')]

        if not self.validateInputs():
            return
        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        if self.schoolids is not None:
            self.createOnlySchoolReports()
        else:
            self.createGPReports()
