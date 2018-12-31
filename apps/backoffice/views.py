from django.shortcuts import render
from django.views import View


class BackOfficeView(View):
    template_name = 'backoffice/export.html'

    def get(self, request):
        return render(request, self.template_name)
