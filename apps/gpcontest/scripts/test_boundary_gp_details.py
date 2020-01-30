from gpcontest.reports.boundary_details import *


def run():
    print("Starting check of all GPs..")
    # district report
    result = get_details(2, 420, "SD", 201906, 202003)
    print("DISTRICT result========")
    print(result)
    print("==============================")
    # Block report
    result = get_details(2, 499, "SB", 201906, 202003)
    print("BLOCK result=======")
    print(result)
    print("==============================")
    # GP report
    result = get_details(2, 1982, "GP",201906, 202003)
    print("GP result=======")
    print(result)
    print("==============================")
    print("DONE")