import sys
import jinja2
import os
from jinja2 import Template
import shutil
import sys
from schools.models import Institution
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    basefiledir = os.getcwd()+"/apps/gpcontest/"
    templatedir = "/templates/"
    outputdir = "/pdfs/"
    out_file = "gpsummarysheet"
    template_name = "GPContestSummarySheet.tex"
    template_file = basefiledir+templatedir+template_name
    build_d = basefiledir+"/build"

    def add_arguments(self, parser):
        parser.add_argument('gpid')


    def initiatelatex(self):
        if not os.path.exists(self.build_d):  # create the build directory if not existing
            os.makedirs(self.build_d)
        if not os.path.exists(self.basefiledir+self.outputdir):  # create the pdf directory if not existing
            os.makedirs(self.basefiledir+self.outputdir)
        latex_jinja_env = jinja2.Environment(
            variable_start_string = '{{',
            variable_end_string = '}}',
            comment_start_string = '\#{',
            comment_end_string = '}',
            line_comment_prefix = '%%',
            trim_blocks = True,
            autoescape = False,
            loader = jinja2.FileSystemLoader(os.path.abspath('/'))
        )
        template = latex_jinja_env.get_template(self.template_file)
        return template

    def getBoundaryInfo(self, gpid):
        boundaryqs = Institution.objects.filter(gp_id=gpid).values('admin1_id__name','admin2_id__name','gp_id__const_ward_name').distinct()
        if boundaryqs.count() > 1:
            print("More than one set of values returned for gpid: "+str(gpid)+" : "+str(boundaryqs))
            exit
        print(boundaryqs)
        for boundary in boundaryqs:
            boundaryinfo= {"district": boundary["admin1_id__name"].title(), "block": boundary["admin2_id__name"].title(), "gpid":str(gpid), "gpname":boundary["gp_id__const_ward_name"].title()}
        return boundaryinfo

    def getSchoolInfo(self, gpid):
        schoolinfo = []
        schoolsqs = Institution.objects.filter(gp_id=gpid).values('name','dise_id__school_code').distinct()
        for school in schoolsqs:
            schoolinfo.append({"schoolname": school['name'], "disecode": school['dise_id__school_code']})
        return schoolinfo

    def handle(self, *args, **options):
        gpid = options.get("gpid")
        self.out_file = self.out_file+"_"+str(gpid)
        template = self.initiatelatex()
        boundaryinfo = self.getBoundaryInfo(gpid)
        schoolinfo = self.getSchoolInfo(gpid)
        renderer_template = template.render(boundaryinfo=boundaryinfo, schools=schoolinfo)

        with open(self.out_file+".tex", "w", encoding='utf-8') as f:  # saves tex_code to outpout file
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(os.path.realpath(self.build_d), os.path.realpath(self.out_file)))
        shutil.copy2(self.build_d+"/"+self.out_file+".pdf", os.path.dirname(self.basefiledir+self.outputdir))
