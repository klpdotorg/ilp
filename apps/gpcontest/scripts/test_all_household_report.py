from gpcontest.reports.household_report import *


def run():
    print("Household report summary")
    scores = get_all_boundary_HH_reports(7,'201806', '201903')
    print(scores)
