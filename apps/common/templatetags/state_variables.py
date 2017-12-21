from django import template
from django.conf import settings


register = template.Library()


# States and values

STATE = {
    'ilp': {
        'name': 'Karnataka',
        'short_form': 'KLP',
        'long_form': 'Karnataka Learning Partnership',
        'email': 'info@.ilp.org.in'
    },
    'ka': {
        'name': 'Karnataka',
        'short_form': 'KLP',
        'long_form': 'Karnataka Learning Partnership',
        'email': 'info@.klp.org.in'
    },
    'od': {
        'name': 'Odisha',
        'short_form': 'OLP',
        'long_form': 'Odisha Learning Partnership',
        'email': 'info@.olp.org.in'
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
