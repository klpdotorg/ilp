from gpcontest.reports.household_report import *


def run():
    print("Household report for districts")
    scores = get_hh_reports_for_districts(7, 2, [415], '201906', '202003')
    print(scores)
    print("========================================")
    print("Household report for GPs")
    get_hh_reports_for_gps(7, 2, [872,1030,1055], '201906', '202003')
    print("========================================")
    print("Household report for school ids")
    scores = get_hh_reports_for_school_ids(7, 2, [3854,6946], '201906', '202003')
    print(scores)
    print("========================================")
   

