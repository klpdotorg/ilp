from django import template
from django.conf import settings

from common.state_codes import STATES


register = template.Library()


@register.simple_tag(takes_context=True)
def get_state_value(context, variable):

    try:
        print("State_ID is: ", settings.ILP_STATE_ID)
        value = STATES[settings.ILP_STATE_ID][variable]
    except KeyError:
        return ''  # If the state or variable is not found, return an empty
        # string
    else:
        return value
