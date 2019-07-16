import uuid
import os
import threading

from django.shortcuts import render
from django.views import View
from django.conf import settings

from boundary.models import BoundaryStateCode

from backoffice.forms import ExportForm
from backoffice.utils import (
    get_assessment_field_names, create_csv_and_move
)


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

            file_path = settings.MEDIA_ROOT + '/backoffice-data/'
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            try:
                threading.Thread(target=create_csv_and_move, args=(
                    data['survey'], data['district'], data['block'],
                    data['cluster'], data['school'], data['from_year'],
                    data['from_month'], data['to_month'], data['to_year'],
                    file_id + '.csv', field_names
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


class GPContestValidatorView(View):
    """
    View that validates GP contest raw data excel file
    """
    template_name = 'backoffice/gpcontest_validator.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        return render(
            request,
            self.template_name,
            {
                'errors': ['Unknown error occured. Please contact KLP team at dev@klp.org.in'],
                'success': ['All rows passed']
            }
        )
