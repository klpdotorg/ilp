from django.conf import settings

from rest_framework import serializers
from schools.models import Institution

from common.serializers import ILPSerializer, InstitutionTypeSerializer
from boundary.serializers import (
    BoundarySerializer, ElectionBoundarySerializer
)


class InstitutionSerializer(ILPSerializer):
    boundary = BoundarySerializer(source='admin3')
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')
    type = InstitutionTypeSerializer(source='institution_type')

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'boundary', 'admin1', 'admin2',
            'admin3', 'type'
        )


class InstitutionInfoSerializer(ILPSerializer):
    mgmt = serializers.CharField(source='management.name')
    cat = serializers.CharField(source='category.name')
    moi = serializers.SerializerMethodField()
    sex = serializers.CharField(source='gender.name')
    address_full = serializers.CharField(source='address')
    identifiers = serializers.SerializerMethodField()
    admin1 = BoundarySerializer('admin1')
    admin2 = BoundarySerializer('admin2')
    admin3 = BoundarySerializer('admin3')
    parliament = serializers.SerializerMethodField()
    assembly = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    type = InstitutionTypeSerializer(source='institution_type')
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()

    # TODO: Add
    # buses.
    # images.
    # basic_facilities
    # has_volunteer_activities

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address_full', 'cat', 'mgmt', 'moi', 'sex',
            'landmark', 'identifiers', 'admin1', 'admin2', 'admin3',
            'parliament', 'dise_code', 'assembly', 'ward', 'type',
            'num_boys', 'num_girls'
        )

    def get_moi(self, obj):
        lang = obj.institutionlanguage_set.first()
        if lang:
            return lang.moi.name
        return None

    def get_identifiers(self, obj):
        return ', '.join(filter(None, [
            obj.instidentification, obj.instidentification2
        ])) or None

    def get_parliament(self, obj):
        if obj.mp is None:
            return None
        return ElectionBoundarySerializer(obj.mp).data

    def get_assembly(self, obj):
        if obj.mla is None:
            return None
        return ElectionBoundarySerializer(obj.mla).data

    def get_ward(self, obj):
        if obj.ward is None:
            return None
        return ElectionBoundarySerializer(obj.ward).data

    def get_gender_counts(self, obj):
        if (
            obj.institutionstugendercount_set.filter(
                academic_year=settings.DEFAULT_ACADEMIC_YEAR).exists()
        ):
            return obj.institutionstugendercount_set.\
                get(academic_year=settings.DEFAULT_ACADEMIC_YEAR)
        return None

    def get_num_boys(self, obj):
        gender_count = self.get_gender_counts(obj)
        if gender_count:
            return gender_count.num_boys
        return None

    def get_num_girls(self, obj):
        gender_count = self.get_gender_counts(obj)
        if gender_count:
            return gender_count.num_girls
        return None
