from django.conf import settings

from rest_framework import serializers

from schools.models import (
    Institution, Management, PinCode, InstitutionCategory,
    InstitutionAggregation
)

from common.serializers import ILPSerializer, InstitutionTypeSerializer
from common.models import (
    InstitutionGender, Status, AcademicYear
)
from boundary.serializers import (
    BoundarySerializer, ElectionBoundarySerializer
)


class InstitutionSerializer(ILPSerializer):
    boundary = BoundarySerializer(source='admin3')
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')
    type = InstitutionTypeSerializer(source='institution_type')
    dise_code = serializers.CharField(source="dise.school_code")
    moi = serializers.SerializerMethodField()
    parliament = serializers.SerializerMethodField()
    assembly = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    sex = serializers.CharField(source='gender.name')
    identifiers = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'boundary', 'admin1', 'admin2',
            'admin3', 'type', 'category', 'dise', 'dise_code',
            'area', 'landmark', 'pincode', 'gender', 'management',
            'moi', 'sex', 'identifiers', 'admin1', 'admin2', 'admin3',
            'parliament', 'assembly', 'ward', 'type', 'num_boys', 'num_girls',
            'last_verified_year', 'institution_languages'
        )

    def get_moi(self, obj):
        lang = obj.institution_languages.first()
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
        if obj.institutionstugendercount_set.filter(
                academic_year=settings.DEFAULT_ACADEMIC_YEAR).exists():
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


class InstitutionCreateSerializer(ILPSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all()
    )
    gender = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionGender.objects.all()
    )
    management = serializers.PrimaryKeyRelatedField(
        queryset=Management.objects.all()
    )
    address = serializers.CharField(default=None)
    area = serializers.CharField(default=None)
    pincode = serializers.PrimaryKeyRelatedField(
        queryset=PinCode.objects.all(), default=None
    )
    landmark = serializers.CharField(default=None)
    last_verified_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), required=True)

    class Meta:
        model = Institution
        fields = (
            'id', 'admin3', 'dise', 'name', 'category', 'gender',
            'status', 'institution_type', 'management', 'address',
            'area', 'pincode', 'landmark', 'last_verified_year',
        )

    def save(self, **kwargs):
        admin3 = self.validated_data['admin3']
        return Institution.objects.create(
            admin0=admin3.parent.parent.parent,
            admin1=admin3.parent.parent,
            admin2=admin3.parent,
            **self.validated_data
        )


class InstitutionCategorySerializer(ILPSerializer):
    type = InstitutionTypeSerializer(source='institution_type')

    class Meta:
        model = InstitutionCategory
        fields = (
            'id', 'name', 'type'
        )


class InstitutionManagementSerializer(ILPSerializer):

    class Meta:
        model = Management
        fields = (
            'id', 'name'
        )


class SchoolDemographicsSerializer(ILPSerializer):
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    mt_profile = serializers.DictField(source='get_mt_profile')
    acyear = serializers.IntegerField(source='dise.academic_year.char_id')
    num_boys_dise = serializers.SerializerMethodField()
    num_girls_dise = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = ('id', 'name', 'gender', 'mt_profile', 'management', 'num_boys_dise',
                  'num_girls_dise', 'num_boys', 'num_girls', 'acyear')

   
    def get_gender_counts(self, obj):
        print("get_gender_counts", obj.institutionstugendercount_set)
        if obj.institutionstugendercount_set.filter(
                academic_year=settings.DEFAULT_ACADEMIC_YEAR).exists():
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

    def get_num_boys_dise(self, obj):
        print("get_num_boys_dise obj is: ", obj.dise)
        num_boys = obj.dise.total_boys
        return num_boys
    
    def get_num_girls_dise(self, obj):
        num_girls = obj.dise.total_girls
        return num_girls
