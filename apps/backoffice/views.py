import csv
import time
import threading

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from backoffice.forms import ExportForm
from backoffice.utils import (
    get_assessment_field_data, get_assessment_field_names,
    create_csv_and_move
)
from boundary.models import BoundaryStateCode
from assessments.models import Survey


class BackOfficeView(View):
    template_name = 'backoffice/export.html'

    def get(self, request):
        states = BoundaryStateCode.objects.all()
        year = list(range(2016, 2020))
        month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        return render(request, self.template_name,
                      {'states': states, 'year': year, 'month': month})

    def post(self, request):
        form = ExportForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            field_names = get_assessment_field_names(
                data['survey']
            )
            try:
                threading.Thread(target=create_csv_and_move, args=(
                    data['survey'], data['district'], data['block'],
                    data['cluster'], data['school'], data['year'],
                    data['month'], 'data.csv', field_names
                )).start()
            except:
                print("Error: unable to start thread")
            return render(request, self.template_name)
        else:
            return render(request, self.template_name, 
                          {'form_errors': form.errors})
        return response
