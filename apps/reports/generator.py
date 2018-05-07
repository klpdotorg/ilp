import django_filters
from reports.reports import ReportOne, ReportTwo,GPMathContestReport

reportlist = {"report_one":ReportOne,"report_two": ReportTwo,"gp_contest_report": GPMathContestReport}

def generate_report(report_format, report_type, output_name, *args):
    try:
        r = reportlist[report_type]
        report = r(*args)
        report.generate(report_format, output_name)
        report.save()
        print('success')
    except KeyError:
        print("Invalid report type")

    except ValueError :
        print("Error in Report generation")
