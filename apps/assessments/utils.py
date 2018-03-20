import json

from assessments.models import SurveyTagMapping


def get_surveys(tag_name=None, state=None, jsonNeeded=False):
    qset = SurveyTagMapping.objects.all()
    res = []
    if tag_name:
        qset = qset.filter(tag=tag_name)
    if state:
        qset = qset.filter(survey__admin0__name=state)
    for qs_dict in qset.values('survey_id', 'survey__name'):
        res.append(
            {'id': qs_dict['survey_id'], "name": qs_dict['survey__name']}
        )
    if jsonNeeded:
        return json.dumps({"surveys": res})
    return res
