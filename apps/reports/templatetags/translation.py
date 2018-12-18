from django.utils.translation import gettext as _
from django import template

register = template.Library()
@register.filter(name='translate')
def translate(text):  
    return _(text.strip())

@register.filter(name='to_float')
def to_float(value):
    return float(value)