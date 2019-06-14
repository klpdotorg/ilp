from gpcontest.reports.generate_boundary_reports import *
import datetime

def run():
    print("=================================================")
    print("MULTIPLE BOUNDARY REPORTS")
    print(datetime.datetime.now().time())
    all = generate_all_district_reports(
                            2, 201806, 201903, True)
    print(datetime.datetime.now().time())
    print(all)