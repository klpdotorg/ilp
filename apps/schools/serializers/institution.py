from django.conf import settings

from rest_framework import serializers

from schools.models import (
    Institution, Management, PinCode, InstitutionCategory,
    InstitutionAggregation, InstitutionLanguage, Student, StudentStudentGroupRelation, StudentGroup
)
from common.serializers import ILPSerializer, InstitutionTypeSerializer
from common.models import (
    InstitutionGender, Status, AcademicYear, Language
)
from boundary.serializers import (
    BoundarySerializer, ElectionBoundarySerializer
)

from dise import dise_constants


class LeanInstitutionSummarySerializer(ILPSerializer):
    ''' returns just id, name, dise_code and geo-locations'''
    dise_code = serializers.SerializerMethodField()
    type = serializers.CharField(source='institution_type.char_id')

    class Meta:
        model = Institution
        fields = (
            'id', 'dise_code', 'name', 'type'
        )
    
    def get_dise_code(self, obj):
        if obj.dise is not None:
            return obj.dise.school_code
        else:
            return None


class InstitutionSummarySerializer(ILPSerializer):
    ''' This class returns just a summarized list of institution info
    to show in the schools popup of the maps page on the frontend '''
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')
    type = InstitutionTypeSerializer(source='institution_type')
    dise_code = serializers.SerializerMethodField()
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    library_yn = serializers.SerializerMethodField()
    playground = serializers.SerializerMethodField()
    computer_aided_learnin_lab = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = (
            'id', 'dise_code', 'name', 'admin1', 'admin2',
            'admin3', 'type', 'category', 'dise',
            'type', 'num_boys', 'num_girls', 'library_yn',
            'playground', 'computer_aided_learnin_lab'
        )

    def get_dise_code(self, obj):
        if obj.dise is not None:
            return obj.dise.school_code
        else:
            return None

    def get_gender_counts(self, obj):
        if obj.institutionstugendercount_set.filter(
                academic_year=settings.DEFAULT_ACADEMIC_YEAR).exists():
            return obj.institutionstugendercount_set.\
                get(academic_year=settings.DEFAULT_ACADEMIC_YEAR)
        return None
    
    def get_num_boys(self, obj):
        ''' This method always returns the num of boys from DISE if 
        that exists. Else, it tries the KLP DB '''
        num_boys = 0
        if(obj.dise is not None):
            num_boys = obj.dise.total_boys
        else:
            gender_count = self.get_gender_counts(obj)
            if gender_count:
                num_boys = gender_count.num_boys
            else:
                return None
        return num_boys

    def get_num_girls(self, obj):
        ''' This method always returns the num of girls from DISE if that exists.
        Else it tries the KLP DB (data may be outdated) '''
        num_girls = 0
        if(obj.dise is not None):
            num_girls = obj.dise.total_girls
        else:
            gender_count = self.get_gender_counts(obj)
            if gender_count:
                num_girls = gender_count.num_girls
            else:
                return None
        return num_girls
    
    def get_library_yn(self, obj):
        if obj.dise is not None:
            if obj.dise.library_yn == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None

    def get_playground(self, obj):
        if obj.dise is not None:
            if obj.dise.playground == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None
    
    def get_computer_aided_learnin_lab(self, obj):
        if obj.dise is not None:
            if obj.dise.computer_aided_learnin_lab == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None


class InstitutionSerializer(ILPSerializer):
    boundary = BoundarySerializer(source='admin3')
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')
    type = InstitutionTypeSerializer(source='institution_type')
    dise_code = serializers.SerializerMethodField()
    moi = serializers.SerializerMethodField()
    parliament = serializers.SerializerMethodField()
    assembly = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    sex = serializers.CharField(source='gender.name')
    identifiers = serializers.SerializerMethodField()
    images = serializers.ListField(source='get_images')
    grades = serializers.DictField(source='get_grades')
    institution_languages = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'boundary', 'admin1', 'admin2',
            'admin3', 'type', 'category', 'dise', 'dise_code',
            'area', 'landmark', 'pincode', 'gender', 'management',
            'moi', 'sex', 'identifiers', 'admin1', 'admin2', 'admin3',
            'parliament', 'assembly', 'ward', 'type', 'num_boys', 'num_girls',
            'last_verified_year', 'institution_languages', 'route_information',
            'images', 'grades'
        )

    def get_dise_code(self, obj):
        if obj.dise is not None:
            return obj.dise.school_code
        else:
            return None

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

    def get_institution_languages(self, obj):
        langs = [
            inst_lang.moi.char_id for inst_lang in obj.institution_languages.all()]
        return langs


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
    area = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.PrimaryKeyRelatedField(
        queryset=PinCode.objects.all(), default=None, allow_null=True
    )
    landmark = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_verified_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), required=True)
    institution_languages = serializers.ListField(write_only=True)

    class Meta:
        model = Institution
        fields = (
            'id', 'admin3', 'dise', 'name', 'category', 'gender',
            'status', 'institution_type', 'management', 'address',
            'area', 'pincode', 'landmark', 'last_verified_year',
            'institution_languages'
        )

    def save(self, *args, **kwargs):
        admin3 = self.validated_data['admin3']
        langs = self.validated_data.pop('institution_languages')
        inst = Institution.objects.create(
            admin0=admin3.parent.parent.parent,
            admin1=admin3.parent.parent,
            admin2=admin3.parent,
            **self.validated_data
        )
        for lang in langs:
            lang = Language.objects.get(char_id=lang)
            inst_lang = InstitutionLanguage.objects.create(
                institution=inst, moi=lang)
            inst.institution_languages.add(inst_lang)
        return inst

    def update(self, instance, validated_data):
        print("Institution update validated_data is: ", validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.area = validated_data.get('area', instance.area)
        instance.landmark = validated_data.get('landmark', instance.landmark)
        instance.pincode = validated_data.get('pincode', instance.pincode)
        instance.category = validated_data.get('category', instance.category)
        instance.management = validated_data.get(
            'management', instance.management)
        instance.last_verified_year = validated_data.get(
            'last_verified_year', instance.last_verified_year)
        instance.institution_type = validated_data.get(
            'institution_type', instance.institution_type
        )

        old_inst_langs = instance.institution_languages.all()
        for inst_lang in old_inst_langs:
            lang = Language.objects.get(char_id=inst_lang.moi.char_id)
            inst_lang = InstitutionLanguage.objects.get(
                institution=instance, moi=lang)
            inst_lang.delete()

        langs = self.validated_data.pop('institution_languages', None)
        if langs is not None:
            for lang in langs:
                lang = Language.objects.get(char_id=lang)
                inst_lang, created = InstitutionLanguage.objects.get_or_create(
                    institution=instance, moi=lang)
                instance.institution_languages.add(inst_lang)
        return instance.save()


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

class InstitutionLanguageSerializer(ILPSerializer):

    class Meta:
        model = InstitutionLanguage
        fields = (
            'id', 'moi'
        )

class SchoolDemographicsSerializer(ILPSerializer):
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    mt_profile = serializers.DictField(source='get_mt_profile')
    acyear = serializers.SerializerMethodField()
    num_boys_dise = serializers.SerializerMethodField()
    num_girls_dise = serializers.SerializerMethodField()
    moi = serializers.SerializerMethodField()
    
    class Meta:
        model = Institution
        fields = ('id', 'name', 'gender', 'mt_profile', 'management', 'num_boys_dise',
                  'num_girls_dise', 'num_boys', 'num_girls', 'acyear','moi')

    #Subha S: 28/02 Adding this method in specifically for the compare flow of the frontend. 
    # Frontend merges demographics and finance endpoints of each school and shows the info.
    # There's no MOI data being propagated from these two endpoints. So adding it in. 
    # We should have a broader conversation on whether we should compare the whole of the institution summary
    # instead of just demographics and finance.
    def get_moi(self, obj):
        lang = obj.institution_languages.first()
        if lang:
            return lang.moi.name
        return None

    def get_acyear(self, obj):
        return settings.DEFAULT_ACADEMIC_YEAR

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
        if obj.dise is not None:
            num_boys = obj.dise.total_boys
            return num_boys
        else:
            return None
    
    def get_num_girls_dise(self, obj):
        if obj.dise is not None:
            num_girls = obj.dise.total_girls
            return num_girls
        else:
            return None

class PreschoolInfraSerializer(ILPSerializer):
    
    num_boys = serializers.SerializerMethodField()
    num_girls = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()

    def get_facilities(self, obj):
        data = {}
        all_infra_details = obj.surveyinstitutionquestionagg_set.all()
        for infra_group in all_infra_details:
            if infra_group.question_key not in data:
                data[infra_group.question_key] = {}
            data[infra_group.question_key][infra_group.question_desc]=infra_group.score
        return data
    
    # def get_ang_facility_details(self, obj):
    #     data = {}
    #     ang_infras = obj.anganwadiinfraagg_set.all().select_related('ai_metric')
    #     for infra in ang_infras:
    #         if infra.ai_group not in data:
    #             data[infra.ai_group] = {}
    #         data[infra.ai_group][infra.ai_metric.value.strip()] = (infra.perc_score == 100)
    #     return data

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

    class Meta:
        model = Institution
        fields = ('id', 'name', 'num_boys', 'num_girls', 'facilities')


class SchoolInfraSerializer(ILPSerializer):
   
    tot_clrooms = serializers.IntegerField(source='dise.tot_clrooms')
    lowest_class = serializers.IntegerField(source='dise.lowest_class')
    highest_class = serializers.IntegerField(source='dise.highest_class')
    teacher_count = serializers.SerializerMethodField()
    no_of_computers = serializers.IntegerField(source="dise.no_of_computers")
    toilet_common = serializers.IntegerField(source="dise.toilet_common")
    toilet_boys = serializers.IntegerField(source="dise.toilet_boys")
    toilet_girls = serializers.IntegerField(source="dise.toilet_girls")
    classrooms_in_good_condition=serializers.IntegerField(source="dise.classrooms_in_good_condition")
    classrooms_require_major_repair=serializers.IntegerField(source="dise.classrooms_require_major_repair")
    classrooms_require_minor_repair=serializers.IntegerField(source="dise.classrooms_require_minor_repair")
    electricity=serializers.SerializerMethodField()
    boundary_wall = serializers.SerializerMethodField()
    library_yn = serializers.SerializerMethodField()
    playground = serializers.SerializerMethodField()
    books_in_library= serializers.IntegerField(source="dise.books_in_library")
    computer_aided_learnin_lab = serializers.SerializerMethodField()
    medical_checkup = serializers.SerializerMethodField()
    status_of_mdm = serializers.SerializerMethodField()
    ramps = serializers.SerializerMethodField()
    building_status = serializers.SerializerMethodField()
    drinking_water=serializers.SerializerMethodField()
    # dise_rte = serializers.CharField(source='dise_info.get_rte_details')
    # facilities = serializers.CharField(source='dise_info.get_facility_details')


    class Meta:
        model = Institution
        fields = ('id', 'name', 'building_status', 'drinking_water', 'tot_clrooms', 'lowest_class',
            'highest_class', 'status', 'teacher_count', 'no_of_computers',
            'toilet_common', 'toilet_boys', 'toilet_girls', 'classrooms_in_good_condition', 'classrooms_require_major_repair',
            'classrooms_require_minor_repair', 'electricity', 'boundary_wall',
            'library_yn', 'books_in_library', 'computer_aided_learnin_lab',
            'medical_checkup', 'status_of_mdm', 'ramps','playground'
            )

    def get_building_status(self, obj):
        if obj.dise is not None:
            bldg = obj.dise.building_status
            value = ""
            if bldg == dise_constants.BLDG_PRIVATE:
                value = dise_constants.BLDG_TXT_PRIVATE
            elif bldg == dise_constants.BLDG_RENTED:
                value = dise_constants.BLDG_TXT_RENTED
            elif bldg == dise_constants.BLDG_GOVT:
                value = dise_constants.BLDG_TXT_GOVT
            elif bldg == dise_constants.BLDG_GOVT_RENTFREE:
                value = dise_constants.BLDG_TXT_GOVT_RENTFREE
            elif bldg == dise_constants.BLDG_NONE:
                value = dise_constants.BLDG_TXT_NONE
            elif bldg == dise_constants.BLDG_DILAPIDATED:
                value = dise_constants.BLDG_TXT_BLDG_DILAPIDATED
            elif bldg == dise_constants.BLDG_UNDER_CONST:
                value = dise_constants.BLDG_TXT_BLDG_UNDER_CONST
            return value
        else:
            return None

    def get_teacher_count(self, obj):
        if obj.dise is not None:
            return obj.dise.male_tch + obj.dise.female_tch
        else:
            return None

    def get_library_yn(self, obj):
        if obj.dise is not None:
            if obj.dise.library_yn == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None

    def get_playground(self, obj):
        if obj.dise is not None:
            if obj.dise.playground== dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None

    def get_status_of_mdm(self, obj):
        if obj.dise is not None:
            if obj.dise.status_of_mdm == dise_constants.MDM_NOT_APPLICABLE:
                return dise_constants.MDM_TXT_NOT_APPLICABLE
            elif obj.dise.status_of_mdm == dise_constants.MDM_NOT_PROVIDED:
                return dise_constants.MDM_TXT_NOT_PROVIDED
            elif obj.dise.status_of_mdm == dise_constants.MDM_PROVIDED_PREP_SCHOOL:
                return dise_constants.MDM_TXT_PROVIDED_PREP_SCHOOL
            elif obj.dise.status_of_mdm == dise_constants.MDM_PROVIDED_NOTPREP_SCHOOL:
                return dise_constants.MDM_TXT_PROVIDED_NOTPREP_SCHOOL
        else:
            return None
    
    def get_boundary_wall(self, obj):
        if obj.dise is not None:
            if obj.dise.boundary_wall == dise_constants.BOUND_WALL_NA:
                return dise_constants.BOUND_WALL_TXT_NA
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_PUCCA:
                return dise_constants.BOUND_WALL_TXT_PUCCA
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_PUCCABROKEN:
                return dise_constants.BOUND_WALL_TXT_PUCCABROKEN
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_BARBEDWIRE:
                return dise_constants.BOUND_WALL_TXT_BARBEDWIRE
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_HEDGES:
                return dise_constants.BOUND_WALL_TXT_HEDGES
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_NONE:
                return dise_constants.BOUND_WALL_TXT_NONE
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_OTHERS:
                return dise_constants.BOUND_WALL_TXT_OTHERS
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_PARTIAL:
                return dise_constants.BOUND_WALL_TXT_PARTIAL
            elif obj.dise.boundary_wall == dise_constants.BOUND_WALL_UNDER_CONST:
                return dise_constants.BOUND_WALL_TXT_UNDER_CONST
    
    def get_building_status(self, obj):
        pass
    
    def get_electricity(self, obj):
        if obj.dise is not None:
            if obj.dise.electricity == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None
    
    def get_drinking_water(self,obj):
        if obj.dise is not None:
            if obj.dise.drinking_water == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None
    
    def get_medical_checkup(self, obj):
        if obj.dise is not None:
            if obj.dise.medical_checkup == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None

    def get_ramps(self,obj):
        if obj.dise is not None:
            if obj.dise.ramps == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None

    def get_computer_aided_learnin_lab(self, obj):
        if obj.dise is not None:
            if obj.dise.computer_aided_learnin_lab == dise_constants.AVAILABLE:
                return dise_constants.YES
            else:
                return dise_constants.NO
        else:
            return None


class SchoolFinanceSerializer(ILPSerializer):
    sg_recd_dise = serializers.IntegerField(source="dise.school_dev_grant_recd")
    sg_expnd_dise = serializers.CharField(source="dise.school_dev_grant_expnd")
    tlm_recd_dise = serializers.IntegerField(source="dise.tlm_grant_recd")
    tlm_expnd_dise = serializers.CharField(source="dise.tlm_grant_expnd")
    classroom_count = serializers.IntegerField(source='dise.tot_clrooms')
    teacher_count = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = ('id', 'name', 'sg_recd_dise', 'sg_expnd_dise',
        'tlm_recd_dise', 'tlm_expnd_dise', 'classroom_count', 'teacher_count')

    def get_teacher_count(self, obj):
        if obj.dise is not None:
            return obj.dise.male_tch + obj.dise.female_tch
        else:
            return None


