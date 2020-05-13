from django import forms

from schools.models import Institution
from boundary.models import Boundary, BoundaryType
from assessments.models import Survey
from common.models import AcademicYear


class ExportForm(forms.Form):
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
    # from_date = forms.DateField(input_formats=['%Y-%m-%d'])
    # to_date = forms.DateField(input_formats=['%Y-%m-%d'])
    from_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        required=True)
    to_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        required=True)
