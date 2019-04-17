import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime


class Command(BaseCommand):
    basefiledir = os.path.dirname(os.path.realpath(__file__))+"/gpcontest"
    templatedir = "/templates/"
    outputdir = "/pdfs/"
    out_file = "GPSchool_Report"
    template_name = "GPSchoolReport.tex"
    template_file = basefiledir+templatedir+template_name
    build_d = basefiledir+"/build"

    def initiatelatex(self):
        # create the build directory if not existing
        if not os.path.exists(self.build_d):
            os.makedirs(self.build_d)
        # create the pdf directory if not existing
        if not os.path.exists(self.basefiledir+self.outputdir):
            os.makedirs(self.basefiledir+self.outputdir)
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
        template = latex_jinja_env.get_template(self.template_file)
        return template

    def handle(self, *args, **options):
        template = self.initiatelatex()
        year = int(datetime.today().strftime('%Y'))
        if year >= 6 :
            year = str(year)+"-"+str(year+1)
        else:
            year = str(year-1)+"-"+str(year)
        info = {"year": year}
        schoolinfo = {"district": "Dname",
                       "block": "bname",
                       "gpname": "GPNAME",
                       "schoolname": "SNAME",
                       "klpid": 1234,
                       "gpid": 123}

        assessmentinfo = {"class":4, "stucount": 100, "questions":[]}
        self.out_file = self.out_file+"_"+str(schoolinfo["klpid"])+"_"+str(assessmentinfo["class"])
        for numquestion in range (0,20):
            assessmentinfo["questions"].append({"text":"questiontext"+str(numquestion), "numcorrect":numquestion, "percount":numquestion})
        print(assessmentinfo)
        renderer_template = template.render(info=info, schoolinfo=schoolinfo, assessmentinfo=assessmentinfo)

        # saves tex_code to outpout file
        with open(self.out_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
            os.path.realpath(self.build_d), os.path.realpath(self.out_file)))
        print(os.path.dirname(self.basefiledir+self.outputdir))
        shutil.copy2(self.build_d+"/"+self.out_file+".pdf", os.path.dirname(
            self.basefiledir+self.outputdir))
        print("finished copying")
