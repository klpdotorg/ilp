import datetime, os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View

from .links import send_link
from .models import Reports, Tracking
from .reportlist import reportlist
# Create your views here.

def view_report(request, report_id, tracking_id='default'):
    report = get_object_or_404(Reports, link_id=report_id)
    data = report.data

    tracker = Tracking.objects.get(track_id=tracking_id, report_id__link_id=report_id)
    tracker.visit_count += 1
    tracker.visited_at = datetime.datetime.now()
    tracker.save()

    return render(request, 'reports/{}.html'.format(report.report_type), context={'data':data})

def download_report(request, report_id, tracking_id='default'):
    report_model = get_object_or_404(Reports, link_id=report_id)
    report = reportlist[report_model.report_type](data=report_model.data)
    pdf = report.get_pdf()
    filename = report_model.report_type+datetime.datetime.now().strftime("%d%m%y")+'.pdf'

    tracker = Tracking.objects.get(track_id=tracking_id, report_id__link_id=report_id)
    tracker.download_count += 1
    tracker.downloaded_at = datetime.datetime.now()
    tracker.save()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename=' + filename
    return response

class SendReport(View):
    def get(self,request):
        return render(request, 'reports/send_report.html', context={'reports':reportlist})

    def post(self,request):
        report_type = request.POST.get('report_type')
        report_from = request.POST.get('from')
        report_to = request.POST.get('to')
        recipients = request.POST.get('recipients').split(',')
        dry = True #request.POST.get('dry_run')
        report_args = {}
        for i in reportlist[report_type].parameters:
            report_args[i] = request.POST.get(i)
        report_args['report_from'] = report_from
        report_args['report_to'] = report_to

        send_link(report_type, report_args, recipients, dry_run=dry)

        return HttpResponse((report_type, report_args, recipients))
