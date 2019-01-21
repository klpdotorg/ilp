import uuid
import threading

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from backoffice.forms import ExportForm
from django.conf import settings

from backoffice.utils import (
    get_assessment_field_names, create_csv_and_move
)
from boundary.models import BoundaryStateCode


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
            file_id = str(uuid.uuid1())
            try:
                threading.Thread(target=create_csv_and_move, args=(
                    data['survey'], data['district'], data['block'],
                    data['cluster'], data['school'], data['year'],
                    data['month'], file_id + '.csv', field_names
                )).start()
            except Exception as e:
                return render(
                    request, self.template_name,
                    {'file_error': (
                        "There is an error in generating the file:", e)}
                )
            file_url = (
                settings.MEDIA_URL + 'backoffice-data/' + file_id + '.csv'
            )
            return render(request, self.template_name, {'file_url': file_url})
        return render(
            request, self.template_name, {'form_errors': form.errors}
        )
