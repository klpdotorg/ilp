from django import forms

from schools.models import Institution
from boundary.models import Boundary, BoundaryType
from assessments.models import Survey


class ExportForm(forms.Form):
    survey = forms.ModelChoiceField(
        queryset=Survey.objects.all())
    district = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_DISTRICT), 
        required=False)
    block = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_BLOCK),
        required=False)
    cluster = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_CLUSTER),
        required=False)
    school = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False)
    from_date = forms.DateField(input_formats=['%Y-%m-%d'], required=False)
    to_date = forms.DateField(input_formats=['%Y-%m-%d'], required=False)
    # from_year = forms.IntegerField(
    #     max_value=2020, min_value=2016, required=False)
    # from_month = forms.IntegerField(
    #     required=False)
    # to_year = forms.IntegerField(
    #     max_value=2020, min_value=2016, required=False)
    # to_month = forms.IntegerField(
    #     required=False)
