from django.shortcuts import render
from django.views import View

from backoffice.forms import ExportForm
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
        return render(request, self.template_name)
