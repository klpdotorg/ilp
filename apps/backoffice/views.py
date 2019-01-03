import csv

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from backoffice.forms import ExportForm
from backoffice.utils import (
    get_assessment_field_data, get_assessment_field_names
)
from boundary.models import Boundary, BoundaryType
from assessments.models import Survey


class BackOfficeView(View):
    template_name = 'backoffice/export.html'

    def get(self, request):
        admin1s = Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_DISTRICT)
        surveys = Survey.objects.all()
        year = list(range(2016, 2020))
        month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        return render(request, self.template_name,
                      {'admin1s': admin1s, 'surveys': surveys,
                       'year': year, 'month': month})

    def post(self, request):
        form = ExportForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            field_names = get_assessment_field_names(
                data['survey']
            )
            field_data = get_assessment_field_data(
                data['survey'], data['district'],
                data['block'], data['cluster'],
                data['school'], data['year'], data['month']
            )

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'

            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            for datum in field_data:
                writer.writerow(datum)
        else:
            return render(request, self.template_name, 
                          {'form_errors': form.errors})
        return response
