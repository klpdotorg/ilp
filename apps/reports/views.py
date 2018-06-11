import datetime, os, csv
from io import TextIOWrapper

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View

from .links import send_link
from .models import Reports, Tracking
from .reportlist import reportlist
# Create your views here.

def view_report(request, report_id, tracking_id='default'):
    try:
        report = Reports.objects.get(link_id=report_id)
        data = report.data
    except Reports.DoesNotExist:
        return render(request, 'reports/not_found.html', context={'data': report_id})

    try:
        tracker = Tracking.objects.get(track_id=tracking_id, report_id__link_id=report_id)
        tracker.visit_count += 1
        tracker.visited_at = datetime.datetime.now()
        tracker.save()
    except Tracking.DoesNotExist:
        pass

    if request.GET.get('lang') == 'kannada':
        return render(request, 'reports/{}kannada.html'.format(report.report_type), context={'data':data})
    else:
        return render(request, 'reports/{}.html'.format(report.report_type), context={'data':data})

def download_report(request, report_id, tracking_id='default'):
    try:
        report = Reports.objects.get(link_id=report_id)
    except Reports.DoesNotExist:
        return render(request, 'reports/not_found.html', context={'data': report_id})

    report = reportlist[report_model.report_type](data=report_model.data)
    pdf = report.get_pdf()
    filename = report_model.report_type+datetime.datetime.now().strftime("%d%m%y")+'.pdf'

    try:
        tracker = Tracking.objects.get(track_id=tracking_id, report_id__link_id=report_id)
        tracker.download_count += 1
        tracker.downloaded_at = datetime.datetime.now()
        tracker.save()
    except Tracking.DoesNotExist:
        pass

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
        dry = request.POST.get('dry_run')
        print(dry)
        recipients = TextIOWrapper(request.FILES['recipients'].file, encoding=request.encoding)
        reader = csv.reader(recipients)
        is_head_set = False
        head = []
        params = dict(report_from=report_from, report_to=report_to)

        for person in reader:
            if not is_head_set:
                head = person
                is_head_set = True
            else:
                if person[0] and person[2]:
                    arg = {'name': self.getValue(person, head,'first_name'),
                           'number':self.getValue(person, head,'mobile_number'),
                    }
                    for i in reportlist[report_type].parameters:
                        params[i] = self.getValue(person, head,i)
                    try:
                        send_link(report_type,params, arg, dry_run=dry)
                    except ValueError as e:
                        print(e.args[0])
        report_args=[]
        return HttpResponse((report_type, report_args, recipients))

    def getValue(self, person, head, i):

        index = head.index(i)
        value = person[index]
        return value
