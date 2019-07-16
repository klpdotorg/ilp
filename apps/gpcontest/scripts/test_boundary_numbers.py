from gpcontest.reports.generate_boundary_reports import *
import datetime

def run():
    print("=================================================")
    print("MULTIPLE BOUNDARY REPORTS")
    
    print("Generating district AND block reports...")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_all_district_reports(
                            2, 201806, 201903, True)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")
    print("Generating block reports..")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_all_block_reports(
                            2, 201806, 201903)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")
    print("Generating block reports for district 420..")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_block_reports_for_district(
                            2, [420, 416], 201806, 201903)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")