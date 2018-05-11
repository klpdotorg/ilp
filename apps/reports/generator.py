import django_filters
from reports.reports import ReportOne,GPMathContestReport
import sys

reportlist = {"report_one":ReportOne, "gp_contest_report": GPMathContestReport}



def generate_report_internal(report_format, report_type, output_name, args):
    try:
        r = reportlist[report_type]
        report = r()
        report.parse_args(args)
        report.generate(report_format, output_name)
        result = report.save()
        return result.id
    except KeyError:
        sys.stderr.write("{} is not a valid report type\n".format(report_type))
        raise
    except ValueError :
        sys.stderr.write("Error in Report generation\n")
        raise

def generate_report(report_format, report_type, output_name, args):
    try:
        rid = generate_report_internal(report_format, report_type, output_name, args)
        print ("Report created. Id is {} \n".format(rid))

    except (KeyError, ValueError) as e:
        sys.exit(-2)
