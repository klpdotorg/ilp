import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import ElectionBoundary, Boundary
from schools.models import Institution
from gpcontest.reports import generate_report, school_compute_numbers


class Command(BaseCommand):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates GP and School Reports, pass --gpid [commaseparated gpids]\
            surveyid startyearmonth endyearmonth--onlygp (True/False) \
            --sid [comma separated schoolids]'
    assessmentorder = ["class4", "class5", "class6"]
    assessmentnames = {"class4": {"name": "Class 4 Assessment", "class": 4},
                       "class5": {"name": "Class 5 Assessment", "class": 5},
                       "class6": {"name": "Class 6 Assessment", "class": 6}}
    now = date.today()
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir+"/generated_files/gpreports/"+str(now)+"/GPReports"
    gpoutputdir = "gpreports"
    schooloutputdir = "schoolreports"
    gp_out_file_prefix = "GPReport"
    school_out_file_prefix = "SchoolReport"

    gpsummary = {} 
    schoolsummary = []
    # gp_template_name = "GPReport.tex"
    # school_template_name = "GPSchoolReport.tex"
    # gp_template_file = basefiledir+templatedir+gp_template_name
    # school_template_file = basefiledir+templatedir+school_template_name

    templates = {"school": {"template": "GPSchoolReport.tex", "latex": None},
                 "gp": {"template": "GPReport.tex", "latex": None},
                 "gpsummary": {"template": "GPReportGPSummary.tex",
                               "latex": None},
                 "schoolsummary": {"template": "GPReportSchoolSummary.tex",
                                   "latex": None}}

    build_d = basefiledir+"/build/"
    gp = {}
    survey = None
    gpids = None
    surveyid = None
    onlygp = False
    schoolids = None
    districtids = None
    colour = "bw"
    imagesdir = basefiledir+"/apps/gpcontest/images/"
    mergereport = True

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--gpid', nargs='?')
        parser.add_argument('--onlygp', nargs='?')
        parser.add_argument('--sid', nargs='?')
        parser.add_argument('--districtid', nargs='?')
        parser.add_argument('--mergereport', nargs='?', default=True)
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

    def createGPReports(self):
        data = {}
        if self.gpids is None:
            data = generate_report.generate_all_reports(self.surveyid,
                                                        self.startyearmonth,
                                                        self.endyearmonth)
        else:
            data["gp_info"] = {}
            for gp in self.gpids:
                data["gp_info"][gp] = generate_report.generate_gp_summary(
                        gp, self.surveyid, self.startyearmonth,
                        self.endyearmonth)

        # print("All GPs data is")
        print(data, file=self.utf8stdout)
        for gp in data["gp_info"]:
            print(gp)
            num_contests = len(data["gp_info"][gp])
            suffix = ""
            count = 0
            for contestdate in data["gp_info"][gp]:
                count += 1
                if num_contests > 1:
                    suffix = "_"+str(count)
                outputdir, gppdf = self.createGPPdfs(gp,
                                         data["gp_info"][gp][contestdate],
                                         self.templates["gp"]["latex"], suffix)

                if not self.onlygp:
                    # print(gp)
                    schoolpdfs = self.createSchoolReports(gp, outputdir, contestdate, suffix)

                if self.mergereport:
                    combinedFile = "GPContestInformation_"+str(gp)+suffix+".pdf"
                    self.mergeReports(outputdir+"/", gppdf, schoolpdfs, combinedFile)

            self.createSchoolsSummary(outputdir)
        self.createGPSummarySheet()

    def createGPSummarySheet(self):
        for district in self.gpsummary:
            for block in self.gpsummary[district]:
                info = {"date": self.now, "num_gps": len(self.gpsummary[district][block])}
                renderer_template = self.templates["gpsummary"]["latex"].render(
                                                gps=self.gpsummary[district][block], info=info)

                # saves tex_code to outpout file
                outputfile = "GPContestGPSummary"
                with open(outputfile+".tex", "w", encoding='utf-8') as f:
                    f.write(renderer_template)

                os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(outputfile)))
                outputdir = self.outputdir+"/"+district+"/"+block
                shutil.copy2(self.build_d+"/"+outputfile+".pdf", outputdir)
                self.deleteTempFiles([outputfile+".tex",
                             self.build_d+"/"+outputfile+".pdf"])

    def createGPPdfs(self, gpid, gpdata, template, suffix):
        # print(gpdata, file=self.utf8stdout)
        if type(gpdata) is int or type(gpdata) is str:
            return
        gpdata["contestdate"] = gpdata["date"]
        gpinfo = {"gpname": gpdata["gp_name"].capitalize(),
                  "block": gpdata["block"].capitalize(),
                  "district": gpdata["district"].capitalize(),
                  "cluster": gpdata["cluster"].capitalize(),
                  "contestdate": gpdata["contestdate"],
                  "school_count": gpdata["num_schools"],
                  "totalstudents": gpdata["num_students"]}
        assessmentinfo = []
        for assessment in self.assessmentorder:
            if self.assessmentnames[assessment]["name"] in gpdata:
                gpdata[self.assessmentnames[assessment]["name"]]["class"] = self.assessmentnames[assessment]["class"]
                assessmentinfo.append(gpdata[self.assessmentnames[assessment]["name"]])
        # print(assessmentinfo)
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        if "percent_scores" not in gpdata:
            percent_scores = None
        else:
            percent_scores = gpdata["percent_scores"]
        renderer_template = template.render(gpinfo=gpinfo,
                                            assessmentinfo=assessmentinfo,
                                            info=info,
                                            percent_scores=percent_scores)

        output_file = self.gp_out_file_prefix+"_"+str(gpid)+suffix
        outputdir = self.outputdir+"/"+gpdata["district"]+"/"+gpdata["block"]+"/"+str(gpid)
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

        if gpdata["district"] not in self.gpsummary:
            self.gpsummary[gpdata["district"]] = {gpdata["block"]: [{"gpid": gpid,
                               "gpname": gpdata["gp_name"].capitalize(),
                               "contestdate": gpdata["contestdate"],
                               "total_schools": gpdata["num_schools"],
                               "class4_schools": gpdata["class4_num_schools"],
                               "class5_schools": gpdata["class5_num_schools"],
                               "class6_schools": gpdata["class6_num_schools"]}]}
        else:
            if gpdata["block"] in self.gpsummary[gpdata["district"]]:
                self.gpsummary[gpdata["district"]][gpdata["block"]].append({"gpid": gpid,
                               "gpname": gpdata["gp_name"].capitalize(),
                               "contestdate": gpdata["contestdate"],
                               "total_schools": gpdata["num_schools"],
                               "class4_schools": gpdata["class4_num_schools"],
                               "class5_schools": gpdata["class5_num_schools"],
                               "class6_schools": gpdata["class6_num_schools"]})
            else:
                self.gpsummary[gpdata["district"]][gpdata["block"]] = [{"gpid": gpid,
                               "gpname": gpdata["gp_name"].capitalize(),
                               "contestdate": gpdata["contestdate"],
                               "total_schools": gpdata["num_schools"],
                               "class4_schools": gpdata["class4_num_schools"],
                               "class5_schools": gpdata["class5_num_schools"],
                               "class6_schools": gpdata["class6_num_schools"]}]
  
        return outputdir, output_file+".pdf"

    def createGPReportsPerBoundary(self):
        data = {}
        for district in self.districtids:
            gps = Institution.objects.filter(admin1_id=district, gp_id__isnull=False).distinct("gp_id").values("gp_id")
            for gp in gps:
                gpid = gp["gp_id"]
                retdata = generate_report.generate_gp_summary(
                        gpid, self.surveyid, self.startyearmonth, 
                        self.endyearmonth)

                if retdata != {}:
                    data[gpid] = retdata
                else:
                    continue
                num_contests = len(data[gpid])
                suffix = ""
                count = 0
                outputdir = ""
                for contestdate in data[gpid]:
                    count += 1
                    if num_contests > 1:
                        suffix = "_"+str(count)
                    outputdir, gppdf = self.createGPPdfs(gpid,
                                         data[gpid][contestdate],
                                         self.templates["gp"]["latex"], suffix)
                    print(outputdir)

                    if not self.onlygp:
                        schoolpdfs = self.createSchoolReports(gpid, outputdir, contestdate, suffix)

                    if self.mergereport:
                        combinedFile = "GPContestInformation_"+str(gpid)+".pdf"
                        self.mergeReports(outputdir+"/", gppdf, schoolpdfs, combinedFile)

                print(outputdir)
                self.createSchoolsSummary(outputdir)
            self.createGPSummarySheet()


    def createOnlySchoolReports(self):
        school_outputdir = self.outputdir+"/schools/"
        for school in self.schoolids:
            schooldata = school_compute_numbers.get_school_report(
                                       school, self.surveyid,
                                       self.startyearmonth, self.endyearmonth)
            school_builddir = self.build_d+str(self.now) + \
                              "/schools/"+str(school)
            suffix = ""
            count = 0
            num_contests = len(schooldata)
            for contestdate in schooldata:
                count += 1
                if num_contests > 1:
                    suffix = "_"+str(count)
                self.createSchoolPdfs(schooldata[contestdate], school_builddir,
                                      school_outputdir, suffix)
        self.createSchoolsSummary(school_outputdir)

    def createSchoolPdfs(self, schooldata, builddir, outputdir, suffix):
        info = {"imagesdir": self.imagesdir, "year": self.academicyear}
        contestdate = schooldata["date"]
        # print(schooldata, file=self.utf8stdout)
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
                   "contestdate": schooldata["date"],
                   "generated": self.now,
                   "assessmentcounts": {}}
        for assessment in self.assessmentorder:
            summary["assessmentcounts"][self.assessmentnames[assessment]["class"]] = 0
            if self.assessmentnames[assessment]["name"] in schooldata:
                info["classname"] = self.assessmentnames[assessment]["class"]
                assessmentinfo = schooldata[self.assessmentnames[assessment]["name"]]
                summary["assessmentcounts"][self.assessmentnames[assessment]["class"]] = schooldata[self.assessmentnames[assessment]["name"]]["num_students"]
                # print(assessmentinfo, file=self.utf8stdout)
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

        school_file = self.school_out_file_prefix+"_"+str(schoolinfo["klpid"])+suffix+".pdf"
        self.combinePdfs(pdfscreated, school_file, outputdir)
        self.deleteTempFiles(pdfscreated)
        self.schoolsummary.append(summary)
        return school_file

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

    def createSchoolReports(self, gpid, outputdir, gpcontestdate, suffix):
        schoolsdata = school_compute_numbers.get_gp_schools_report(
                gpid, self.surveyid, self.startyearmonth, self.endyearmonth)

        # print(schoolsdata, file=self.utf8stdout)
        schoolpdfs = []
        for schoolid in schoolsdata:
            # print(schoolid)
            num_contests = len(schoolsdata[schoolid])
            if gpcontestdate in schoolsdata[schoolid]:
                schooldata = schoolsdata[schoolid][gpcontestdate]
                # print(schooldata, file=self.utf8stdout)
                school_builddir = self.build_d+str(self.now)+"/"+str(gpid)+"/" +\
                        str(schooldata["school_id"])
                schoolpdf = self.createSchoolPdfs(schooldata, school_builddir, outputdir, suffix)
                schoolpdfs.append(schoolpdf)
        return schoolpdfs

    def createSchoolsSummary(self, outputdir):
        # print(self.schoolsummary)
        info = {"date": self.now, "num_schools": len(self.schoolsummary)}
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
        self.schoolsummary = []

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
        self.mergereport = options.get("mergereport")

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
            self.createOnlySchoolReports()
        elif self.districtids is not None:
            self.createGPReportsPerBoundary()
        else:
            self.createGPReports()

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
