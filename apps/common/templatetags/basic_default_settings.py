from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_dise_url(context):

    try:
        value = settings.DISE_API_BASE_URL
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value

@register.simple_tag(takes_context=True)
def get_dise_app_url(context):
    try:
        value = settings.DISE_APP_URL
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value

@register.simple_tag(takes_context=True)
def get_default_academic_year(context):

    try:
        value = settings.DEFAULT_ACADEMIC_YEAR
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value

@register.simple_tag(takes_context=True)
def get_formatted_default_academic_year(context):
    try:
        value = settings.DEFAULT_ACADEMIC_YEAR
    except KeyError:
        return ''
    else:
        formatted_value = value[0:2] + "-" + value[2:]
        return formatted_value

@register.simple_tag(takes_context=True)
def get_full_dise_academic_year(context):

    try:
        value = settings.DISE_FRONTEND_ACADEMIC_YEAR
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value

@register.simple_tag(takes_context=True)
def get_dise_academic_year(context):

    try:
        value = settings.DISE_ACADEMIC_YEAR
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value