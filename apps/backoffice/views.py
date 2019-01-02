from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from backoffice.forms import ExportForm
from backoffice.utils import (
    get_assessment_field_data, get_assessment_field_names,
    generate_pdf
)
from boundary.models import Boundary, BoundaryType
from assessments.models import Survey


class BackOfficeView(View):
    template_name = 'backoffice/export.html'

    def get(self, request):
        admin1s = Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_DISTRICT)
        surveys = Survey.objects.all()
        return render(request, self.template_name,
                      {'admin1s': admin1s, 'surveys': surveys})

    def post(self, request, *args, **kwargs):
        form = ExportForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            field_names = get_assessment_field_names(cleaned_data['survey'].id)
            field_data = get_assessment_field_data(cleaned_data['survey'].id)
            pdf = generate_pdf()
            return HttpResponse(pdf, content_type='application/pdf')
        return render(request, self.template_name)
