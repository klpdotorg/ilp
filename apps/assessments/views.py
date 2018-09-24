import json

from django.template.response import TemplateResponse
from django.views.generic.detail import DetailView

from schools.models import Institution
from assessments.models import (AnswerGroup_Institution, InstitutionImages)
from assessments.utils import get_surveys
from django.conf import settings


class SYSView(DetailView):
    template_name = 'sys_form.html'
    model = Institution

    def get_context_data(self, **kwargs):
        context = super(SYSView, self).get_context_data(**kwargs)
        school = context['object']
        context['school_type'] = 'school' if school.institution_type.char_id == "primary" else 'preschool'
        context['total_verified_stories'] = AnswerGroup_Institution.objects.filter(questiongroup_id__in=[1,6],
                                            is_verified=True).count()
        imageCount = InstitutionImages.objects.filter(answergroup__questiongroup__survey=5).count()
        context['total_images'] = imageCount
        return context


def gka_dashboard(request):
    """ Renders the GKA dashboard """

    STATE_MAPPING = {
        'ka': 'Karnataka',
        'od': 'Odisha'
    }
    try:
        current_state = STATE_MAPPING[settings.ILP_STATE_ID]
    except KeyError:
        current_state = None
    response = {
        'surveys': json.dumps(
            get_surveys(state=current_state, jsonNeeded=True)
        )
    }

    return TemplateResponse(request, 'gka_dashboard.html', response)

def gp_contest_dashboard(request):
    """ Renders the GP Contest Dashboard """

    return TemplateResponse(request, 'gp_contest_dashboard.html', {})
