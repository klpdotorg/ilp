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

    return render(request, 'reports/{}'.format(report_model.report_type), context=data)
