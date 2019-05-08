from gpcontest.reports.generate_report import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_all_reports(2, "201806", "201809")
    print(gradewise)
    #result = generate_all_reports(2, "201806", "201901")
    print("=================================================")
