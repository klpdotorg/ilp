import sys
import xlwt
import csv
import os
from datetime import datetime, date
import sys
from schools.models import Institution
from boundary.models import BoundaryStateCode, Boundary
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    basefiledir = os.getcwd()
    now = date.today()
    base_outputdir = basefiledir+"/generated_files/csvs/" + str(now) + "/AppreciationLetters/"
    output = {}
    filename = "District_Contacts_" + str(now) + ".xls"
    district_designations = {
        "DDPI (Admin)": "ಉಪನಿರ್ದೇಶಕರು (ಆಡಳಿತ)",
        "DDPI (Development)": " ಉಪನಿರ್ದೇಶಕರು (ಅಭಿವೃದ್ಧಿ)",
        "DYPC": " ಉಪಯೋಜನಾಧಿಕಾರಿಗಳು",
        "GKA Nodal Officer": "ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನದ ನೋಡಲ್ ಅಧಿಕಾರಿಗಳು",
        "CEO": "ಮುಖ್ಯ ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು",
        "DC": "ಜಿಲ್ಲಾಧಿಕಾರಿಗಳ ಹೆಸರು"
    }
    block_designations = ["ಕ್ಷೇತ್ರ ಶಿಕ್ಷಣಾಧಿಕಾರಿಗಳು","ಕ್ಷೇತ್ರ ಸಮನ್ವಯಾಧಿಕಾರಿಗಳ ಹೆಸರು","ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನದ ನೋಡಲ್ ಅಧಿಕಾರಿಗಳು","ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು"]
    gp_designations = {
        "Gram Panchyath President": "ಗ್ರಾಮ ಪಂಚಾಯತಿ ಅಧ್ಯಕ್ಷರು",
        "Panchayat development officer": "ಗ್ರಾಮ ಪಂಚಾಯತಿ  ಅಭಿವೃದ್ಧಿ ಅಧಿಕಾರಿಗಳು",
        "Cluster Resource Person": "ಕ್ಷೇತ್ರ ಸಂಪನ್ಮೂಲ ವ್ಯಕ್ತಿ",
        "Gram Panchyath Team Leader": "ಗಣಿತ ಸ್ಪರ್ಧಾ ತಂಡದ ನಾಯಕ"
    }
    def add_arguments(self, parser):
        parser.add_argument('--districtids', nargs='?')
        #parser.add_argument('--stateid', nargs='?')


    def getDistrictInfo(self, districtids):
        if districtids is None:
            if stateid is None:
                print("Either --stateid or --districtids have to be passed")
                return False
        else:
            districtids = [int(x) for x in districtids.split(',')]
            districts = Boundary.objects.filter(id__in=districtids).values("id", "name")

        for district in districts:
            district_info = {"blocks":{}, "gps": {}}
            district_info["id"]=district["id"]
            district_info["name"] = district["name"]
            # Get all blocks for this district
            blocks = Boundary.objects.filter(parent_id__in=districtids).values("id", "name")
            for block in blocks:
                district_info["blocks"][block["id"]]=block["name"]
            # Get all GPs for this district
            gps = Institution.objects.filter(admin1_id__in=districtids, gp_id__isnull=False).values("gp_id", "gp_id__const_ward_name", "admin2_id", "admin2_id__name")
            for gp in gps:
                district_info["gps"][gp["gp_id"]] = {
                    "name": gp["gp_id__const_ward_name"],
                    "block_id": gp["admin2_id"],
                    "block_name": gp["admin2_id__name"]
                }

            if district["id"] not in self.output:
                self.output[district["id"]] = district_info
        return True


    def createDesignationSheets(self):
        outputdir = None
        book = xlwt.Workbook()
        sheet = book.add_sheet("District")
        csvtempfile = open('tempfilename.csv', 'w', encoding='utf8')
        writer = csv.writer(csvtempfile)
        writer.writerow(["id", "name","designation_english", "designation_kannada", "officer_name"])
        for key,value in self.output.items():
            outputdir = self.base_outputdir + str(key)
            # First write the district file name 
            dt_filename = outputdir + "/" + "District_Designations_" + str(self.now) + ".xls"
            if not os.path.exists(outputdir):  # create the pdf directory if not existing
                os.makedirs(outputdir)
            for key2, value2 in self.district_designations.items():
                writer.writerow([key, value["name"], key2, value2, " "])
        csvtempfile.close()
        with open('tempfilename.csv', 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    sheet.write(r, c, col)
        book.save(dt_filename)
        self.deleteTempFiles(['tempfilename.csv'])
        
        # Now write the blocks file
        blocks_filename = outputdir + "/" + "Block_Designations_" + str(self.now) + ".xls"
        book = xlwt.Workbook()
        sheet = book.add_sheet("Block")
        csvtempfile = open('tempfilename.csv', 'w', encoding='utf8')
        writer = csv.writer(csvtempfile)
        writer.writerow(["block_id", "block_name","designation_kannada", "officer_name"])
        for district_id, value in self.output.items():
            for block_id, block_name in value["blocks"].items():
                for designation in self.block_designations:
                    writer.writerow([block_id, block_name, designation, " "])
        csvtempfile.close()
        with open('tempfilename.csv', 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    sheet.write(r, c, col)
        book.save(blocks_filename)
        self.deleteTempFiles(['tempfilename.csv'])

        # Now write the Gps file
        gps_filename = outputdir + "/" + "GP_Designations_" + str(self.now) + ".xls"
        book = xlwt.Workbook()
        sheet = book.add_sheet("GP")
        csvtempfile = open('tempfilename.csv', 'w', encoding='utf8')
        writer = csv.writer(csvtempfile)
        writer.writerow(["block_id", "block_name","gp_id", "gp_name", "designation_english", "designation_kannada", "officer_name"])
        for district_id, value in self.output.items():
            for gp_id, gp_values in value["gps"].items():
                for designation_english, designation_kannada in self.gp_designations.items():
                    writer.writerow([gp_values["block_id"], gp_values["block_name"], gp_id, gp_values["name"], designation_english, designation_kannada, " "])
        csvtempfile.close()
        with open('tempfilename.csv', 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    sheet.write(r, c, col)
        book.save(gps_filename)
        self.deleteTempFiles(['tempfilename.csv'])


       

    def deleteTempFiles(self, tempFiles):
        for f in tempFiles:
            os.remove(f)
 
    def handle(self, *args, **options):
        if not os.path.exists(self.base_outputdir):  # create the pdf directory if not existing
            os.makedirs(self.base_outputdir)
        districtids = options.get("districtids", None)
        #stateid = options.get("stateid", None)
        done = self.getDistrictInfo(districtids)
        if done:
            self.createDesignationSheets()
