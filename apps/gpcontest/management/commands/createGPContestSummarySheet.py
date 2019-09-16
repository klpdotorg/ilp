import sys
import jinja2
import os
from jinja2 import Template
from datetime import datetime, date
from django.db.models import Q
import shutil
import sys
from schools.models import Institution
from django.core.management.base import BaseCommand
from . import baseReport 


class Command(BaseCommand, baseReport.CommonUtils):
    now = date.today()
    basefiledir = os.getcwd()
    pdfsdir = "/generated_files/gpreports/"+str(now)+"/"
    templatedir = "/apps/gpcontest/templates/"
    out_file = "GPSummarysheet"
    template_name = "GPContestSummarySheet.tex"
    template_file = basefiledir+templatedir+template_name
    build_d = basefiledir+"/build"
    gpids = None
    outputdir = "preContestSummary"
    schoolinfo = {}

    def add_arguments(self, parser):
        parser.add_argument('--gpids', nargs='?')
        parser.add_argument('--districtids', nargs='?')
        parser.add_argument('--blockids', nargs='?')


    def getSchoolInfo(self, boundaries=None, gpids=None ):
        if boundaries is not None:
            schools = Institution.objects.filter(Q(admin1_id__in = boundaries) | Q(admin2_id__in = boundaries), gp_id__isnull= False).values('admin1_id__name', 'admin2_id__name', 'gp_id__const_ward_name', 'name', 'dise_id__school_code', 'id', 'gp_id').distinct()
        if gpids is not None:
            schools = Institution.objects.filter(gp_id__in=gpids).values('admin1_id__name', 'admin2_id__name', 'admin3_id__name', 'gp_id__const_ward_name', 'name', 'dise_id__school_code', 'id', 'gp_id').distinct()

        for school in schools:
            school["name"] = school["name"].replace("&","\&")
            school["name"] = school["name"].replace("_"," ")
            #print("SCHOOL NAME IS: "+school["name"])
            if school["admin1_id__name"] not in self.schoolinfo:
                self.schoolinfo[school["admin1_id__name"]] = {school["admin2_id__name"]:{school["gp_id__const_ward_name"]: {"id": school["gp_id"], "schools": [{"schoolname": school['name'], "disecode": school['dise_id__school_code']}]}}}
            elif school["admin2_id__name"] not in self.schoolinfo[school["admin1_id__name"]]:
                self.schoolinfo[school["admin1_id__name"]][school["admin2_id__name"]] = {school["gp_id__const_ward_name"]: {"id": school["gp_id"], "schools": [{"schoolname": school['name'], "disecode": school['dise_id__school_code']}]}}
            elif school["gp_id__const_ward_name"] not in self.schoolinfo[school["admin1_id__name"]][school["admin2_id__name"]] :
                self.schoolinfo[school["admin1_id__name"]][school["admin2_id__name"]][school["gp_id__const_ward_name"]] = {"id": school["gp_id"], "schools": [{"schoolname": school['name'], "disecode": school['dise_id__school_code']}]}
            else:
                self.schoolinfo[school["admin1_id__name"]][school["admin2_id__name"]][school["gp_id__const_ward_name"]]["schools"].append({"schoolname": school['name'], "disecode": school['dise_id__school_code']})


    def createSummaryReports(self):
        template = self.initiatelatex()
        for district in self.schoolinfo:
            for block in self.schoolinfo[district]:
                for gp in self.schoolinfo[district][block]:
                    gpid = str(self.schoolinfo[district][block][gp]["id"])
                    out_file = self.out_file+"_"+gpid
                    #print(district+" "+block+" "+gpid+" "+gp)
                    boundaryinfo = {"district": district.title(), "block": block.title(), "gpid":gpid, "gpname":gp.title()}
                    schoolinfo = self.schoolinfo[district][block][gp]["schools"]

                    outputdir = self.basefiledir+self.pdfsdir+self.outputdir+"/"+district+"/"+block+"/"
                    if not os.path.exists(outputdir):  # create the pdf directory if not existing
                        os.makedirs(outputdir)
                    renderer_template = template.render(boundaryinfo=boundaryinfo, schools=schoolinfo)

                    with open(out_file+".tex", "w", encoding='utf-8') as f:  # saves tex_code to outpout file
                        f.write(renderer_template)

                    os.system("xelatex -output-directory {} {}".format(os.path.realpath(self.build_d), os.path.realpath(out_file)))
                    shutil.copy2(self.build_d+"/"+out_file+".pdf", os.path.dirname(outputdir))
                    self.deleteTempFiles([out_file+".tex",
                             self.build_d+"/"+out_file+".pdf"])


    def handle(self, *args, **options):
        gpids = options.get("gpids")
        districtids = options.get("districtids")
        blockids = options.get("blockids")

        if gpids is None and blockids is None and districtids is None:
            print("Enter one of the parameters: --gpids, --districtids or --blockids")
            return

        if districtids is not None:
            self.districtids = [int(x) for x in districtids.split(',')]
            self.getSchoolInfo(self.districtids, None)

        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
            self.getSchoolInfo(None, self.gpids)

        if blockids is not None:
            self.blockids = [int(x) for x in blockids.split(',')]
            self.getSchoolInfo(self.blockids, None)

        self.createSummaryReports()

        os.system('tar -cvf '+self.basefiledir+self.pdfsdir+'/'+self.outputdir+'.tar '+self.basefiledir+self.pdfsdir+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
