from gpcontest.reports.boundary_details import *


def run():
    print("Starting check of all GPs..")
    result = get_details(2, 420, 201906, 202003)
    print(result)
    print("DONE")