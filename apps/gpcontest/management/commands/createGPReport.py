import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime
from assessments.models import Survey
from boundary.models import ElectionBoundary
from gpcontest.reports import generate_report,school_compute_numbers


class Command(BaseCommand):
    help = 'Creates GP and School Reports, pass --gpid commaseparated gpids surveyid startyearmonth endyearmonth--onlygp (True/False)'
    assessmentnames = {"4": "Class 4 Assessment", "5": "Class 5 Assessment", "6": "Class 6 Assessment"}
    now = datetime.now()
    #basefiledir = os.path.dirname('apps/gpcontest')#os.path.realpath(__file__))+"/../../"
    basefiledir = os.getcwd()+"/apps/gpcontest/"
    templatedir = "templates/"
    outputdir = basefiledir+"/pdfs/"+str(now)
    gpoutputdir = "gpreports"
    schooloutputdir = "schoolreports"
    gp_out_file = "GPReport"
    school_out_file = "SchoolReport"
    gp_template_name = "GPReport.tex"
    school_template_name = "GPSchoolReport.tex"
    gp_template_file = basefiledir+templatedir+gp_template_name
    school_template_file = basefiledir+templatedir+school_template_name
    build_d = basefiledir+"/build"
    gp = {}
    survey = None
    gpids = None
    surveyid = None
    onlygp = False
    imagesdir = basefiledir+"images/"

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--gpid', nargs='?')
        parser.add_argument('--onlygp', nargs='?')

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
        gp_template = latex_jinja_env.get_template(self.gp_template_file)
        school_template = latex_jinja_env.get_template(self.school_template_file)
        return gp_template, school_template

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
                    self.gp[gp] = ElectionBoundary.objects.get(id=gp, const_ward_type='GP')
                except ElectionBoundary.DoesNotExist:
                    print("Invalid gpid: "+str(gp)+" passed")
                    return False
        try:
            self.survey = Survey.objects.get(id=self.surveyid)
        except Survey.DoesNotExist:
            print("Invalid surveyid: "+str(self.surveyid)+" passed")
            return False

        if not self.checkYearMonth(self.startyearmonth):
            print("Start year month format is invalid it should be YYYYMM, "+self.startyearmonth)
            return False

        if not self.checkYearMonth(self.endyearmonth):
            print("End year month format is invalid it should be YYYYMM, "+self.endyearmonth)
            return False

        return True


    def createGPReports(self, gptemplate, schooltemplate):
        data = {}
        if self.gpids is None: 
            data = generate_report.generate_all_reports(self.surveyid, self.startyearmonth,
                                               self.endyearmonth)
        else:
            for gp in self.gpids:
                print(gp)
                data[gp] = generate_report.generate_gp_summary(gp, self.surveyid, self.startyearmonth, self.endyearmonth)
        print(data)
        for gp in data:
            outputdir = self.createGPPdfs(gp, data[gp], gptemplate)
            print(self.onlygp)
            if not self.onlygp:
                self.createSchoolReports(gp, schooltemplate, outputdir)


    def createGPPdfs(self, gpid, gpdata, template):
        if type(gpdata) is int or  type(gpdata) is str:
            return
        date = datetime.today().strftime('%Y-%m-%d')
        gpinfo= {"gpname":gpdata["gp_name"], "block":gpdata["block"], "district":gpdata["district"],"cluster":gpdata["cluster"],"date":date,"school_count":gpdata["num_schools"], "totalstudents": gpdata["num_students"]}
        class4 = gpdata[self.assessmentnames["4"]]
        class5 = gpdata[self.assessmentnames["5"]]
        class6 = gpdata[self.assessmentnames["6"]]
        info = {"imagesdir": self.imagesdir}
        renderer_template = template.render(gpinfo=gpinfo, class4=class4, class5=class5, class6=class6,
                                                info = info)

        output_file = self.gp_out_file+"_"+str(gpid)
        outputdir = self.outputdir+"/"+str(gpid)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        with open(output_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d), os.path.realpath(output_file)))
        print(os.path.dirname(outputdir))
        shutil.copy2(self.build_d+"/"+output_file+".pdf", 
                         outputdir)
        return outputdir
       
           
    def createSchoolReports(self, gpid, template, outputdir):
        #change to passed date
        schoolsdata = school_compute_numbers.get_school_report(gpid, self.surveyid, self.startyearmonth, self.endyearmonth)

        #info = {"year": year}
        info = {"imagesdir": self.imagesdir}
        for schoolid in schoolsdata:
            schooldata = schoolsdata[schoolid]
            schoolinfo = {"district": schooldata["district_name"],
                      "block": schooldata["block_name"],
                      "gpname": schooldata["gp_name"],
                      "schoolname": schooldata["school_name"],
                      "klpid": schooldata["school_id"],
                      "gpid": gpid,
                      "disecode": schooldata["dise_code"]}
            assessmentinfo = {
                    "class4questions" : schooldata[self.assessmentnames["4"]],
                    "class5questions" : schooldata[self.assessmentnames["5"]],
                    "class6questions" : schooldata[self.assessmentnames["6"]]}

            renderer_template = template.render(info=info,
                    schoolinfo=schoolinfo, assessmentinfo=assessmentinfo)
 
            school_out_file = self.school_out_file+"_"+str(schoolinfo["klpid"])
            school_outputdir = outputdir+"/schools"
            if not os.path.exists(school_outputdir):
                os.makedirs(school_outputdir)

            ## saves tex_code to outpout file
            with open(school_out_file+".tex", "w", encoding='utf-8') as f:
                f.write(renderer_template)

            os.system("xelatex -output-directory {} {}".format(
              os.path.realpath(self.build_d), os.path.realpath(school_out_file)))
            print(os.path.dirname(school_outputdir))
            shutil.copy2(self.build_d+"/"+school_out_file+".pdf",
                         school_outputdir)


    def handle(self, *args, **options):
        gpids = options.get("gpid", None)
        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.onlygp = options.get("onlygp", False)

        if not self.validateInputs():
            return
        gp_template,school_template = self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        self.createGPReports(gp_template, school_template)

