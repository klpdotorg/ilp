from schools.models import Institution
from assessments.models import (AnswerGroup_Institution)
from django.views.generic.detail import DetailView

class SYSView(DetailView):
    template_name = 'sys_form.html'
    model = Institution

    def get_context_data(self, **kwargs):
        context = super(SYSView, self).get_context_data(**kwargs)
        school = context['object']
        context['school_type'] = 'school' if school.institution_type.char_id == "primary" else 'preschool' 
        context['total_verified_stories'] = AnswerGroup_Institution.objects.filter(questiongroup_id=6,
                                            is_verified=True).count()
        # context['total_images'] = StoryImage.objects.count()
        return context