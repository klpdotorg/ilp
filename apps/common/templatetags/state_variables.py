from django import template
from django.conf import settings


register = template.Library()


# States and values

STATE = {
    'ilp': {
        'name': 'Karnataka',
        'short_form': 'KLP',
        'long_form': 'Karnataka Learning Partnership',
        'email': 'info@ilp.org.in',
        'site_url': 'https://ilp.org.in',
        'home_logo': '',
        'header_logo': '',
        'footer_logo': ''
    },
    'ka': {
        'name': 'Karnataka',
        'short_form': 'KLP',
        'long_form': 'Karnataka Learning Partnership',
        'email': 'info@klp.org.in',
        'site_url': 'https://klp.org.in',
        'home_logo': '/static/images/home_klp_logo@2x.png',
        'header_logo': '/static/images/KLP_logo@2x.png',
        'footer_logo': '/static/images/KLP_logo_footer@2x.png'
    },
    'od': {
        'name': 'Odisha',
        'short_form': 'OLP',
        'long_form': 'Odisha Learning Partnership',
        'email': 'info@olp.org.in',
        'site_url': 'https://olp.org.in',
        'home_logo': '/static/images/states/od/home_olp_logo@2x.png',
        'header_logo': '/static/images/states/od/OLP_logo@2x.png',
        'footer_logo': '/static/images/states/od/OLP_logo_footer@2x.png'
    },
}


@register.simple_tag(takes_context=True)
def get_state_value(context, variable):

    try:
        value = STATE[settings.ILP_STATE_ID][variable]
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value
