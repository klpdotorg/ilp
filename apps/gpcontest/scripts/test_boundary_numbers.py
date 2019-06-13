from gpcontest.reports.generate_boundary_reports import *


def run():
    print("BOUNDARY REPORTS")
    gradewise = generate_boundary_report(
                            2, 416,
                            201806, 201903)
    print(gradewise)
    print("=================================================")
    print("MULTIPLE BOUNDARY REPORTS")
    all = generate_multiple_bound_reports(
                            2, [416, 420, 539],
                            201806, 201903)
    print(all)