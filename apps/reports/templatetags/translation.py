from django.utils.translation import gettext as _
from django import template

register = template.Library()
@register.filter(name='translate')
def translate(text):  
    return _(text.strip())

@register.filter(name='to_float')
def to_float(value):
    return float(value)

'''This filter is very specific to our JSOn structure of reports. 
If something changes in the JSON, this method will have to change
FIrst argument is a JSOn structure. Second argument is the question_key'''
@register.simple_tag
def questionkey_exists(data, question_key):
    exists = "False"
    for val in data:
        if val["contest"] == question_key:
            exists = "True"
    return exists