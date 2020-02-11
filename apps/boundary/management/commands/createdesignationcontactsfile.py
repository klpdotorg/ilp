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
from assessments.models import SurveyBoundaryQuestionKeyAgg


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
    block_designations = {
        "BEO": "ಕ್ಷೇತ್ರ ಶಿಕ್ಷಣಾಧಿಕಾರಿಗಳು",
        "BRC": "ಕ್ಷೇತ್ರ ಸಮನ್ವಯಾಧಿಕಾರಿಗಳ ಹೆಸರು",
        "GKA Nodal Officer": "ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನದ ನೋಡಲ್ ಅಧಿಕಾರಿಗಳು",
        "EO": "ಕಾರ್ಯನಿರ್ವಾಹಕ ಅಧಿಕಾರಿಗಳು"
    }
    gp_designations = {
        "Gram Panchyath President": "ಗ್ರಾಮ ಪಂಚಾಯತಿ ಅಧ್ಯಕ್ಷರು",
        "Panchayat development officer": "ಗ್ರಾಮ ಪಂಚಾಯತಿ  ಅಭಿವೃದ್ಧಿ ಅಧಿಕಾರಿಗಳು",
        "Cluster Resource Person": "ಕ್ಷೇತ್ರ ಸಂಪನ್ಮೂಲ ವ್ಯಕ್ತಿ",
        "Gram Panchyath Team Leader": "ಗಣಿತ ಸ್ಪರ್ಧಾ ತಂಡದ ನಾಯಕ"
    }
    def add_arguments(self, parser):
        parser.add_argument('--districtids', nargs='?')
        parser.add_argument('--from_yearmonth', nargs='?')
        parser.add_argument('--to_yearmonth', nargs='?')

    def getDistrictInfo(self, districtids, from_yearmonth, to_yearmonth):
        if districtids is None:
            if from_yearmonth is None or to_yearmonth is None:
                print("Please enter from and to dates in yyyymm format")
                return False
            # Get all distinct district ids
            districtids = SurveyBoundaryQuestionKeyAgg.objects.filter(
                yearmonth__gte=from_yearmonth).filter(
                    yearmonth__lte=to_yearmonth).filter(
                        boundary_id__boundary_type='SD').distinct(
                            'boundary_id').values('boundary_id')                    
        else:
            districtids = [int(x) for x in districtids.split(',')]
            districts = Boundary.objects.filter(id__in=districtids).values("id", "name")

        for district in districts:
            district_info = {"blocks":{}, "gps": {}}
            district_info["id"]=district["id"]
            district_info["name"] = district["name"]
            # Get all blocks for this district
            blocks = Boundary.objects.filter(parent_id=int(district["id"])).values("id", "name", "parent_id", "parent_id__name")
            for block in blocks:
                block_info={}
                block_info["name"] = block["name"]
                block_info["district_id"] = block["parent_id"]
                block_info["district_name"] = block["parent_id__name"]
                district_info["blocks"][block["id"]] = block_info

            # Get all GPs for this district
            gps = Institution.objects.filter(admin1_id=int(district["id"]), gp_id__isnull=False).values("gp_id", "gp_id__const_ward_name", "admin2_id", "admin2_id__name")
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
      
        for key, value in self.output.items():
            outputdir = self.base_outputdir + str(key)
            # First write the district file name 
            dt_filename_xls = outputdir + "/" + "District_Designations_" + str(self.now) + ".xls"
            dt_filename_csv = outputdir + "/" + "District_Designations_" + str(self.now) + ".csv"

            if not os.path.exists(outputdir):  # create the pdf directory if not existing
                os.makedirs(outputdir)
            book = xlwt.Workbook()
            sheet = book.add_sheet("District")
            dt_csv_file = open(dt_filename_csv, 'w', encoding='utf8')
            writer = csv.writer(dt_csv_file)
            writer.writerow(["id", "name","designation_english", "designation_kannada", "officer_name"])   
            for key2, value2 in self.district_designations.items():
                writer.writerow([key, value["name"], key2, value2, " "])
            dt_csv_file.close()
            with open(dt_filename_csv, 'rt', encoding='utf8') as f:
                 reader = csv.reader(f)
                 for r, row in enumerate(reader):
                     for c, col in enumerate(row):
                         sheet.write(r, c, col)
            book.save(dt_filename_xls)
            self.deleteTempFiles([dt_filename_csv])
        
        # Now write the blocks file
       
        for district_id, value in self.output.items():
            blocks_filename_xls = self.base_outputdir + str(district_id) + "/" + "Block_Designations_" + str(self.now) + ".xls"
            blocks_filename_csv = self.base_outputdir + str(district_id) + "/" + "Block_Designations_" + str(self.now) + ".csv"

            # print("Creating block file %s" % blocks_filename_csv)
            block_book = xlwt.Workbook()
            block_sheet = block_book.add_sheet("Block")
            block_csv_file = open(blocks_filename_csv, 'w', encoding='utf8')
            writer = csv.writer(block_csv_file)
            writer.writerow(["district_id", "district_name", "block_id", "block_name","designation_english", "designation_kannada", "officer_name"])
            for block_id, block_info in value["blocks"].items():
                for designation_english, designation_kannada in self.block_designations.items():
                    writer.writerow([block_info["district_id"], block_info["district_name"], block_id, block_info["name"], designation_english, designation_kannada, " "])
            block_csv_file.close()
            # print("Finsihed writng block file %s for district %s " % (block_csv_file, district_id))
            with open(blocks_filename_csv, 'rt', encoding='utf8') as f:
                 reader = csv.reader(f)
                 for r, row in enumerate(reader):
                     for c, col in enumerate(row):
                         block_sheet.write(r, c, col)
            block_book.save(blocks_filename_xls)
            self.deleteTempFiles([blocks_filename_csv])

        # Now write the Gps file
        for district_id, value in self.output.items():
            gps_filename_xls = self.base_outputdir + str(district_id) + "/" + "GP_Designations_" + str(self.now) + ".xls"
            gps_filename_csv = self.base_outputdir + str(district_id) + "/" + "GP_Designations_" + str(self.now) + ".csv"

            gp_book = xlwt.Workbook()
            gp_sheet = gp_book.add_sheet("GP")
            gp_csv_file = open(gps_filename_csv, 'w', encoding='utf8')
            writer = csv.writer(gp_csv_file)
            writer.writerow(["block_id", "block_name", "gp_id", "gp_name", "designation_english", "designation_kannada", "officer_name"])
            # print("Writing file for district %s" % district_id)
            for gp_id, gp_values in value["gps"].items():
                for designation_english, designation_kannada in self.gp_designations.items():
                    writer.writerow([gp_values["block_id"], gp_values["block_name"], gp_id, gp_values["name"], designation_english, designation_kannada, " "])
            gp_csv_file.close()
            print("Finished writing Gps for district %s " % district_id)
            with open(gps_filename_csv, 'rt', encoding='utf8') as f:
                 reader = csv.reader(f)
                 for r, row in enumerate(reader):
                     for c, col in enumerate(row):
                         gp_sheet.write(r, c, col)
            gp_book.save(gps_filename_xls)
            self.deleteTempFiles([gps_filename_csv])


       

    def deleteTempFiles(self, tempFiles):
        for f in tempFiles:
            os.remove(f)
 
    def handle(self, *args, **options):
        if not os.path.exists(self.base_outputdir):  # create the pdf directory if not existing
            os.makedirs(self.base_outputdir)
        districtids = options.get("districtids", None)
        from_yearmonth = options.get("from_yearmonth", None)
        to_yearmonth = options.get("to_yearmonth", None)
        #stateid = options.get("stateid", None)
        done = self.getDistrictInfo(districtids, from_yearmonth, to_yearmonth)
        if done:
            self.createDesignationSheets()
