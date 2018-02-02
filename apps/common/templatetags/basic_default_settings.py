from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_dise_url(context):

    try:
        value = settings.DISE_APP_BASE_URL
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value

@register.simple_tag(takes_context=True)
def get_default_academic_year(context):

    try:
        value = settings.DEFAULT_ACADEMIC_YEAR_FRONTEND
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value
