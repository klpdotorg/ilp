from django.utils.translation import gettext as _
from django import template

register = template.Library()
@register.filter(name='translate')
def translate(text):  
    return _(text.strip())