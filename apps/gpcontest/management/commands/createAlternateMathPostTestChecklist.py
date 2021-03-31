import sys
import jinja2
import os
from jinja2 import Template
from datetime import datetime, date
from django.db.models import Q, F
import shutil
import sys
from schools.models import Institution, Student, StudentStudentGroupRelation
from dise.models import BasicData
from boundary.models import ElectionBoundary
from django.core.management.base import BaseCommand
from . import baseReport 
from assessments.models import AnswerGroup_Student



class Command(BaseCommand, baseReport.CommonUtils):
    now = date.today()
    basefiledir = os.getcwd()
    pdfsdir = "/generated_files/alternatemath/"+str(now)+"/"
    templatedir = "/apps/gpcontest/templates/"
    out_file = "PostTestChildCheckList"
    build_d = basefiledir+"/build"
    gpids = None
    outputdir = "summarysheets"
    childinfo = {}
    templates = {"summary": {"template": "AlternateMathSummaryPostTestChecklist.tex", "latex": None}}
    lang = 'english'
    

    def add_arguments(self, parser):
        parser.add_argument('--gpids', nargs='?')
        parser.add_argument('--districtids', nargs='?')
        parser.add_argument('--blockids', nargs='?')
        parser.add_argument('--lang', nargs='?')


    def getchildinfo(self, boundaries=None, gpids=None ):
        if boundaries is not None:
            # Get all villages for that particular boundary
            qs = AnswerGroup_Student.objects\
                .filter(questiongroup_id__in=[79,80])\
                .filter(
                    Q(student_id__institution_id__admin1_id__in=boundaries) |
                    Q(student_id__institution_id__admin2_id__in=boundaries),
                    student_id__institution_id__gp_id__isnull=False
                    )
            villages = qs.values(
                    district=F('student_id__institution__admin1_id__name'), 
                    block=F('student_id__institution__admin2_id__name'),
                    cluster=F('student_id__institution__admin3_id__name'), 
                    gp_id=F('student_id__institution_id__gp_id'),
                    village=F('student_id__institution_id__village')).distinct()
                    
        # if gpids is not None:
        #     schools = Institution.objects.filter(
        #         gp_id__in=gpids).values(
        #             'admin1_id__name',
        #             'admin2_id__name',
        #             'admin3_id__name',
        #             'gp_id__const_ward_name',
        #             'name', 'dise_id__school_code', 'id', 'gp_id').distinct()
        for village in villages:
            #Child is linked through answergroup student table
            children_in_village = AnswerGroup_Student.objects.filter(
                student_id__institution_id__village=village["village"],
                student_id__institution_id__admin2_id__name=village["block"],
                questiongroup_id__in=[79,80]).values('questiongroup_id', 'student_id').order_by('questiongroup_id')
            # This is the school name
            for child in children_in_village:
                # Put each child's info into the dict.
                if village["village"] is not None:
                    village["village"] = village["village"].replace("&","")
                #Add a try catch here
                stu = Student.objects.get(id=child["student_id"])
                try:
                    stu_stugroup=StudentStudentGroupRelation.objects.get(student=stu,status='AC',academic_year='2021')
                except Exception as e:
                    print("Multiples returned for student id %s, institution id %s " % (stu.id, stu.institution_id))
                # Initialize class to 4. based on q group Id, select the grade because there may be
                # multiples in the DB since our child master is not upto date.
                grade = "4"
                if child['questiongroup_id'] == 80:
                    grade = "5"
                #Add a try catch here
                school = Institution.objects.get(id=stu.institution_id)
                dise = BasicData.objects.get(id=school.dise_id)
                eb = ElectionBoundary.objects.get(id=village["gp_id"])
                school_name = school.name.replace("_"," ")
                #Some children may not have one or the other. So concatenante both
                parent_name = stu.father_name + " " + stu.mother_name
                #print("SCHOOL NAME IS: "+school["name"])
                if village["district"] not in self.childinfo:
                    self.childinfo[village["district"]] = {
                        village["block"]:{
                            village["village"]: {
                                "gp_id": village["gp_id"], 
                                "gp_name": eb.const_ward_name,
                                "cluster": village["cluster"],
                                "children": [
                                    {
                                     "child_id": stu.id,   
                                     "child_name": stu.first_name, 
                                     "parent_name": parent_name,
                                     "father_name": stu.father_name, 
                                     "mother_name": stu.mother_name, 
                                     "schoolname": school.name, 
                                     "disecode": dise.school_code, 
                                     "gender": stu.gender.name[0:1],
                                     "class": grade,
                                     "cluster": village["cluster"]}]}}}
                elif village["block"] not in self.childinfo[village["district"]]:
                    self.childinfo[village["district"]][village["block"]] = {
                            village["village"]: {
                                "gp_id": village["gp_id"], 
                                "gp_name": eb.const_ward_name,
                                "cluster": village["cluster"],
                                "children": [
                                    {"child_id": stu.id, 
                                     "child_name": stu.first_name, 
                                     "parent_name": parent_name,
                                     "father_name": stu.father_name, 
                                     "mother_name": stu.mother_name, 
                                     "schoolname": school.name, 
                                     "class": grade,
                                     "disecode": dise.school_code, 
                                     "gender": stu.gender.name[0:1],
                                     "cluster": village["cluster"]
                                     }]
                                }}
                elif village["village"] not in self.childinfo[village["district"]][village["block"]]:
                    self.childinfo[village["district"]][village["block"]][village["village"]] = {
                                "gp_id": village["gp_id"], 
                                "gp_name": eb.const_ward_name,
                                "cluster": village["cluster"],
                                "children": [
                                    { "child_id": stu.id, 
                                     "child_name": stu.first_name, 
                                     "parent_name": parent_name,
                                     "father_name": stu.father_name, 
                                     "mother_name": stu.mother_name, 
                                     "schoolname": school.name, 
                                     "disecode": dise.school_code, 
                                     "class": grade,
                                     "gender": stu.gender.name[0:1],
                                     "cluster": village["cluster"]
                                     }]
                                }
                else:
                    self.childinfo[village["district"]][village["block"]][village["village"]]["children"].append(
                            {"child_id": stu.id,
                                "child_name": stu.first_name,
                                "parent_name": parent_name,
                                "father_name": stu.father_name,
                                "mother_name": stu.mother_name, 
                                "schoolname": school.name,
                                "class": grade,
                                "disecode": dise.school_code,
                                "gender": stu.gender.name[0:1],
                                "cluster": village["cluster"]
                            })

    def createSummaryReports(self):
        for district in self.childinfo:
            for block in self.childinfo[district]:
                for village in self.childinfo[district][block]:
                    print("Processing village %s in district %s, block %s" % (village, district, block))
                    gpid = str(self.childinfo[district][block][village]["gp_id"])
                    gp_name = str(self.childinfo[district][block][village]["gp_name"])
                    cluster = str(self.childinfo[district][block][village]["cluster"])
                    village_fname = village.replace(" ","")
                    
                    village_fname = village_fname.replace("&","_")
                    # Replace brackets in village name
                    village_fname = village_fname.replace("(","_").replace(")", "_")
                    print("Village name is: " + village_fname)
                    out_file = self.out_file+"_"+village_fname
                    #print(district+" "+block+" "+gpid+" "+gp)
                    boundaryinfo = {"district": district.title(), "block": block.title(), "cluster": cluster.title(), "village": village.title(), "gpid":gpid, "gpname":gp_name.title()}
                    childinfo = self.childinfo[district][block][village]["children"]

                    outputdir = self.basefiledir+self.pdfsdir+self.outputdir+"/"+district+"/"+block+"/"
                    if not os.path.exists(outputdir):  # create the pdf directory if not existing
                        os.makedirs(outputdir)
                    renderer_template = self.templates["summary"]["latex"].render(boundaryinfo=boundaryinfo, children=childinfo)

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
        lang = options.get("lang")

        if lang is not None:
            self.lang = lang

        self.templatedir = self.templatedir+"/"+self.lang+"/"

        if gpids is None and blockids is None and districtids is None:
            print("Enter one of the parameters: --gpids, --districtids or --blockids")
            return

        if districtids is not None:
            self.districtids = [int(x) for x in districtids.split(',')]
            self.getchildinfo(self.districtids, None)

        if gpids is not None:
            self.gpids = [int(x) for x in gpids.split(',')]
            self.getchildinfo(None, self.gpids)

        if blockids is not None:
            self.blockids = [int(x) for x in blockids.split(',')]
            self.getchildinfo(self.blockids, None)

        self.initiatelatex()
        self.createSummaryReports()
        print("Tarring now..")
        os.system('tar -cvf '+self.basefiledir+self.pdfsdir+'/'+self.outputdir+'.tar '+self.basefiledir+self.pdfsdir+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
