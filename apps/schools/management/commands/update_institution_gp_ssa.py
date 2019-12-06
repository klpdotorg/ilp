import os
import math
import sys
import csv
import psycopg2
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings
from common.models import Status
from boundary.models import ElectionBoundary, BoundaryType
from dise.models import BasicData
from schools.models import Institution
from assessments.models import AnswerGroup_Institution
import pandas as pd


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
    state = 2
    districtname = 0
    blockname = 1
    oldgpname = 2
    newgpname = 3
    villagename = 4
    comparevillagename = 5
    schoolname = 6
    schoolid = 7
    disecode = 8
    nogp = []
    nomatchgp = {}
    nomatchvillage = {}
    gpMapCheck = []
    gpAlreadyMapped = []
    gpNewMapped = []
    gpContestNoChange = []
    
    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('--force', default=False)


    def validateSchool(self, row, schoolid, disecode, districtname, blockname):
        print(disecode)
        if math.isnan(disecode):
            print("SHOULD BE HERE")
            try:
                school = Institution.objects.get(id=schoolid,
                        admin1__name__iexact=districtname,
                        admin2__name__iexact=blockname)
                return school, ""
            except Institution.DoesNotExist:
                reason = "Error: Institution object does not exist"
                return None, reason
        try:
            print("HERE")
            school = Institution.objects.get(id=schoolid,
                    dise__school_code=disecode,
                    admin1__name__iexact=districtname,
                    admin2__name__iexact=blockname)
            print("RETURNING")
            return school, ""
        except Institution.DoesNotExist:
            reason = "Error: Institution object does not exist"
            return None, reason

    def checkvillagenames(self, school, villagename, othervillagename):
        if school.village == "":
            if villagename == "":
                return True,""
            else:
                return False, "Village names dont match"
        if villagename != othervillagename:
            return False, "Village names dont match"
        else:
            return True,""

    def getGP(self, schoolid, newgpname, villagename, district, block, schoolname, disecode, schoolobj, force):
        gpassessmentfound = False
        reason = ""
        emptyGP = True

        if schoolobj.gp != None:
            emptyGP = False
            if schoolobj.gp.const_ward_name.lower().strip().startswith(newgpname.lower().strip()):
                return schoolobj.gp.id, "Same GP",""
            else:
                print("No match found: district: "+str(district)+", block: "+str(block)+", schoolname: "+str(schoolname)+", school id: "+str(schoolid)+", disecode: "+str(disecode)+", DB GP name :"+schoolobj.gp.const_ward_name+"("+str(schoolobj.gp.id)+"), new gpname: "+newgpname)
                reason = schoolobj.gp.const_ward_name.lower()+","+newgpname.lower()

            assessmentobj = AnswerGroup_Institution.objects.filter(institution_id=schoolobj.id, questiongroup__survey_id=2)
            if assessmentobj:
                print("Found Contest for school")
                gpassessmentfound = True

        #else:
            #gpassessmentobj = AnswerGroup_Institution.objects.filter(institution_id__gp_id=schoolobj.gp.id, questiongroup__survey_id=2)
            #if gpassessmentobj:
                #print("Found Contest for GP")
                #gpassessmentfound=True

        if gpassessmentfound:
                print("GP Assessment found, not changing GP")
                self.gpContestNoChange.append({schoolobj.id:schoolobj.gp.id})
                return None, "GP Assessment Found, no change", reason

        gpinfo = Institution.objects.filter(admin1__name__iexact=district,
                    admin2__name__iexact=block,
                    gp__isnull=False,
                    gp__const_ward_name__iexact=newgpname).values(
                            'gp__id','gp__const_ward_name').distinct()

        if gpinfo:
            return gpinfo[0]['gp__id'], "GP already exists, assign it",reason
        else:
            print(emptyGP,force)
            if emptyGP or force:
                print("Creating new gp")
                gpid = self.createNewGP(newgpname)
                return gpid, "New GP created, assign it",reason
            else:
                self.gpMapCheck.append({schoolobj.id:schoolobj.gp.id})
                print("Not creating new")
                return None, "GP not created, check",reason

    def createNewGP(self, gpname):
        const_ward_type = BoundaryType.objects.get(char_id='GP')
        try:
            gp = ElectionBoundary.objects.create(const_ward_name=gpname, const_ward_type=const_ward_type, state_id=self.state,  status= self.active_status)
            return gp.id
        except Exception as e:
            print("ERROR: "+str(e))
        return None

    def assignGP(self, school, gp, force):
        if school.gp == None or school.gp == "":
            self.gpNewMapped.append({school.id:gp})
            school.gp_id=gp
            school.save()
            return True, ""
        if school.gp.id == gp:
            self.gpAlreadyMapped.append({school.id:gp})
            return False, "Already Mapped"
        else:
            if force:
                school.gp_id=gp
                school.save()
                self.gpNewMapped.append({school.id:gp})
            else:
                self.gpMapCheck.append({school.id:gp})
                return False, "Check Mapping"

    def parseFile(self, file_name, force):
        df = pd.read_csv(file_name)
        df["Reason"] = ""
        df["GPDATA"] = ""
        df["AssignReason"] = ""
        for index, row in df.iterrows():
            print(row)
            school, reason = self.validateSchool(row, row.schoolid, row.disecode, row.districtname, row.blockname)
            if school == None:
                df.at[index, "Reason"] = reason
                continue
            valid, reason = self.checkvillagenames(school, row.villagename, row.ssa_villagename)
            if not valid:
                df.at[index, "Reason"] = reason
                continue
            gp, reason, gps= self.getGP(row.schoolid, row.ssa_gpname, row.ssa_villagename, row.districtname, row.blockname, row.schoolname, row.disecode, school, force)
            df.at[index, "Reason"] = reason
            df.at[index, "GPDATA"] = gps 
            if gp == None:
                continue
            assigned, assignReason = self.assignGP(school, gp, force)
            df.at[index, "AssignReason"] = assignReason
        df.to_csv("Output_SSA.csv", index=False)

    def printData(self):
        print("List of GP's already mapped:")
        print("School , GP")
        for schoolinfo in self.gpAlreadyMapped:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

        print("List of GP's newly mapped:")
        print("School , GP")
        for schoolinfo in self.gpNewMapped:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

        

        print("List of Schools for which GP mapping has to be changed so Check:"+str(len(self.gpMapCheck)))
        print("School , GP")
        for schoolinfo in self.gpMapCheck:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

        print("List of Schools that had GP Contest so no change:"+str(len(self.gpContestNoChange)))
        print("School, GP")
        for schoolinfo in self.gpContestNoChange:
            (school,gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

                       
    def handle(self, *args, **options):
        file_name = options['filename']
        force = options['force']
     
        if not file_name:
            print ("Please specify a filename with the --filename argument")
            return False

        self.parseFile(file_name, force)
        self.printData()


