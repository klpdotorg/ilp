from django import forms

from schools.models import Institution
from boundary.models import Boundary, BoundaryType
from assessments.models import Survey


class ExportForm(forms.Form):
    survey = forms.ModelChoiceField(
        queryset=Survey.objects.all())
    district = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_DISTRICT))
    block = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_BLOCK))
    cluster = forms.ModelChoiceField(
        queryset=Boundary.objects.filter(
            boundary_type=BoundaryType.SCHOOL_CLUSTER))
    school = forms.ModelChoiceField(
        queryset=Institution.objects.all())
