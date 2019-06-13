from gpcontest.reports.generate_boundary_reports import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_boundary_report(
                            2, 416,
                            201806, 201903):
    print(gradewise)
    print("=================================================")