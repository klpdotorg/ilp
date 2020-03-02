from gpcontest.reports.household_report import *


def run():
    print("Household report summary")
    scores = generate_HHReport_for_boundaries(7,'201806', '201903')
    print(scores)
