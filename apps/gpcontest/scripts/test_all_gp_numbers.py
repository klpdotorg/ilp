from gpcontest.scripts.pandas_gp_numbers_checker import *
from gpcontest.reports.generate_report import get_gps_for_academic_year


def run():
    gps = get_gps_for_academic_year(2, 201906, 202003)
    set_db_connection_params("ilp", "klp")
    for gp in gps:
        check_gp_numbers(gp)
