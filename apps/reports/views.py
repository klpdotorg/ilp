import datetime, os

from django.shortcuts import render

from .models import Reports, Tracking
from .reportlist import reportlist
# Create your views here.

def view_report(request, report_id, tracking_id='default'):
    report_model = Reports.objects.get(link_id=report_id)
    report = reportlist[report_model.report_type]()
    report.parse_args([i+'='+j for i,j in report_model.parameters.items()])
    data = report.get_data()

    tracker = Tracking.objects.get(track_id=tracking_id)
    tracker.visit_count += 1
    tracker.visited_at = datetime.datetime.now()
    tracker.save()

    return render(request, 'reports/{}.html'.format(report_model.report_type), context=data)

def download_report(request, report_id, tracking_id='default'):
    report_model = Reports.objects.get(link_id=report_id)
    report = reportlist[report_model.report_type]()
    report.parse_args([i+'='+j for i,j in report_model.parameters.items()])
    filename = report.get_pdf(report_model.report_type+datetime.datetime.now().strftime("%d%m%y"))

    tracker = Tracking.objects.get(track_id=tracking_id)
    tracker.download_count += 1
    tracker.downloaded_at = datetime.datetime.now()
    tracker.save()

    with open(filename, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filename)
        return response
