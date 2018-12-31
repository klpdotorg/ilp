from django.shortcuts import render
from django.views import View

from boundary.models import Boundary, BoundaryType


class BackOfficeView(View):
    template_name = 'backoffice/export.html'

    def get(self, request):
        admin1s = Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_DISTRICT)
        return render(request, self.template_name, {'admin1s': admin1s})
