from gpcontest.reports.generate_boundary_reports import *
import datetime

def run():
    print("=================================================")
    print("MULTIPLE BOUNDARY REPORTS")
    all = generate_boundary_report(2, 439, 201906, 202005)
    print("RESULT FOR BOUNDARY ID:")
    print(all)
    print("DONE")
    print("=================================================")
    print("Generating district AND block reports...")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_all_district_reports(
                            2, 201906, 202003, True)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")
    print("Generating block reports..")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_all_block_reports(
                            2, 201906, 202003)
    #print(all)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")
    print("Generating block reports for district 420..")
    print("Begin time %s" % datetime.datetime.now().time())
    all = generate_block_reports_for_district(
                            2, [439,425], 201906, 202003)
    #print(all)
    print("End time %s" %datetime.datetime.now().time())
    print("Done")
    print("=================================================")