"""
This file produces a master list of schools to GP mapping. This is utilized
by both the management command & the backoffice page to download the CSV
"""

import sys
import xlwt
import csv
import os
from datetime import datetime, date
import sys
from schools.models import Institution
from boundary.models import BoundaryStateCode


def getSchoolInfo(districtids, stateid):
    schoolinfo = {}
    schools = {}
    if districtids is None:
        if stateid is None:
            print("Either --stateid or --districtids have to be passed")
            return False
        schools = Institution.objects.filter(admin0_id=stateid, gp_id__isnull=False).values("id", "name", "admin1_id__name", "admin2_id__name", "admin3_id__name", "gp_id", "gp_id__const_ward_name", "dise_id__school_code")
    else:
        districtids = [int(x) for x in districtids.split(',')]
        schools = Institution.objects.filter(admin1_id__in=districtids, gp_id__isnull=False).values("id", "name", "admin1_id__name", "admin2_id__name", "admin3_id__name", "gp_id", "gp_id__const_ward_name", "dise_id__school_code")

    for school in schools:
        schoolid = school["id"]
        name = school["name"]
        district = school["admin1_id__name"]
        block = school["admin2_id__name"]
        cluster = school["admin3_id__name"]
        disecode = school["dise_id__school_code"]
        gpid = school["gp_id"]
        gpname = school["gp_id__const_ward_name"]

        if district not in schoolinfo:
            schoolinfo[district] = {block:{cluster:{schoolid:{"name": name, "disecode": disecode, "gpid": gpid, "gpname": gpname}}}}
        else:
            if block not in schoolinfo[district]:
                schoolinfo[district][block] = {cluster:{schoolid:{"name": name, "disecode": disecode, "gpid": gpid, "gpname": gpname}}}
            else:
                if cluster not in schoolinfo[district][block]:
                    schoolinfo[district][block][cluster] = {schoolid:{"name": name, "disecode": disecode, "gpid": gpid, "gpname": gpname}}
                if schoolid not in schoolinfo[district][block][cluster]:
                    schoolinfo[district][block][cluster][schoolid] = {"name": name, "disecode": disecode, "gpid": gpid, "gpname": gpname}
    return schoolinfo


def createSummarySheets(schoolinfo, outputdir, filename):
    filename = outputdir+filename
    book = xlwt.Workbook()
    sheet = book.add_sheet("SchoolInfo")
    csvtempfile = open('tempfilename.csv', 'w')
    writer = csv.writer(csvtempfile)
    writer.writerow(["District", "Block","Cluster", "GP Id", "GP Name","KLP School Id","School Name","DISE CODE"])
    for district in schoolinfo:
        for block in schoolinfo[district]:
            for cluster in schoolinfo[district][block]:
                for schoolid in schoolinfo[district][block][cluster]:
                    writer.writerow([district, block,cluster, schoolinfo[district][block][cluster][schoolid]["gpid"], schoolinfo[district][block][cluster][schoolid]["gpname"], schoolid, self.schoolinfo[district][block][cluster][schoolid]["name"], self.schoolinfo[district][block][cluster][schoolid]["disecode"]])
    csvtempfile.close()
    with open('tempfilename.csv', 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                sheet.write(r, c, col)
    book.save(filename)
    self.deleteTempFiles(['tempfilename.csv'])

def deleteTempFiles(self, tempFiles):
    for f in tempFiles:
        os.remove(f)