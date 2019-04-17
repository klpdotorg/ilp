import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime
from assessments.models import Survey
from boundary.models import ElectionBoundary
from gpcontest.reports import generate_report


class Command(BaseCommand):
    help = 'Creates GP and School Reports, pass --gpid commaseparated gpids --surveyid --startyearmonth --endyearmonth'
    now = datetime.now()
    #basefiledir = os.path.dirname('apps/gpcontest')#os.path.realpath(__file__))+"/../../"
    basefiledir = os.getcwd()+"/apps/gpcontest/"
    templatedir = "templates/"
    outputdir = "pdfs/"+str(now)
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

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--gpid', nargs='?')

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

    def initializeDirs(self):
        self.gpoutputdir = self.basefiledir+self.outputdir+"/"+self.gpoutputdir
        self.schooloutputdir = self.basefiledir+self.outputdir+"/"+self.schooloutputdir
        # create the pdf directory if not existing
        if not os.path.exists(self.gpoutputdir):
            os.makedirs(self.gpoutputdir)
        if not os.path.exists(self.schooloutputdir):
            os.makedirs(self.schooloutputdir)


    def createGPReports(self):
        if self.gpids is None: 
            self.gpids = get_gps_for_academic_year(self.surveyid, self.startyearmonth,
                                               self.endyearmonth)
        for gp in self.gpids:
            gradescores = generate_report.generate_gp_summary(gp, self.surveyid, self.startyearmonth, self.endyearmonth)
            print(gradescores)

           



    def handle(self, *args, **options):
        gpids = options.get("gpid", None)
        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
        self.surveyid = options.get("surveyid", None)
        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)

        if not self.validateInputs():
            return
        gp_template,school_template = self.initiatelatex()
        self.initializeDirs()

        #change to passed date
        #year = int(datetime.today().strftime('%Y'))
        #if year >= 6 :
            #year = str(year)+"-"+str(year+1)
        #else:
            #year = str(year-1)+"-"+str(year)

        self.createGPReports()
        #self.createSchoolReports()
        #info = {"year": year}
        #schoolinfo = {"district": "Dname",
                       #"block": "bname",
                       #"gpname": "GPNAME",
                       #"schoolname": "SNAME",
                       #"klpid": 1234,
                       #"gpid": 123}

        #assessmentinfo = {"class":4, "stucount": 100, "questions":[]}
        #self.out_file = self.out_file+"_"+str(schoolinfo["klpid"])+"_"+str(assessmentinfo["class"])
        #for numquestion in range (0,20):
            #assessmentinfo["questions"].append({"text":"questiontext"+str(numquestion), "numcorrect":numquestion, "percount":numquestion})
        #print(assessmentinfo)
#
        #renderer_template = template.render(info=info, schoolinfo=schoolinfo, assessmentinfo=assessmentinfo)
#
        ## saves tex_code to outpout file
        #with open(self.out_file+".tex", "w", encoding='utf-8') as f:
            #f.write(renderer_template)
#
        #os.system("xelatex -output-directory {} {}".format(
            #os.path.realpath(self.build_d), os.path.realpath(self.out_file)))
        #print(os.path.dirname(self.basefiledir+self.outputdir))
        #shutil.copy2(self.build_d+"/"+self.out_file+".pdf", os.path.dirname(
            #self.basefiledir+self.outputdir))
        #print("finished copying")
