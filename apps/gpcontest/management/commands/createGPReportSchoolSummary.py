import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime


class Command(BaseCommand):
    basefiledir = os.path.dirname(os.path.realpath(__file__))+"/gpcontest"
    templatedir = "/templates/"
    outputdir = "/pdfs/"
    out_file = "gpreport_schoolsummary"
    template_name = "GPReportSchoolSummary.tex"
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
        gpid = options.get("gpid")
        self.out_file = self.out_file+"_"+str(gpid)
        template = self.initiatelatex()
        info = {"date": datetime.today().strftime('%d-%m-%Y')}
        schoolinfo = [{"gpid": "GPID", "gpname": "GPNAME",
                       "schoolname": "SNAME", "dise_code": "DISE",
                       "class4": 10, "class5": 15, "class6": 20,
                       "generated": 45, "sent_to": "Field Name"},
                      {"gpid": "GPID", "gpname": "GPNAME",
                       "schoolname": "SNAME1", "dise_code": "DISE1",
                       "class4": 10, "class5": 15, "class6": 20,
                       "generated": 45, "sent_to": "Field Name"}]
        renderer_template = template.render(schools=schoolinfo, info=info)

        # saves tex_code to outpout file
        with open(self.out_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
            os.path.realpath(self.build_d), os.path.realpath(self.out_file)))
        print(os.path.dirname(self.basefiledir+self.outputdir))
        shutil.copy2(self.build_d+"/"+self.out_file+".pdf", os.path.dirname(
            self.basefiledir+self.outputdir))
        print("finished copying")
