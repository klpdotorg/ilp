from gpcontest.reports.school_compute_numbers import *


def run():
    print("GP School report summary")
    scores = get_gp_schools_report(6386, 2, '201906', '202003')
    print(scores)
    # Test individual school report
    print("Testing individual school report")
    result = get_school_report(6386, 2, '201906', '202003')
    print("=================================================")

   
