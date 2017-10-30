from rest_framework import serializers

from drf_compound_fields.fields import DictField

from common.models import (InstitutionType,
                            Language)
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField


class ILPSerializer(serializers.ModelSerializer):
    # geometry = DictField(source='get_geometry')
    # geometry = GeometrySerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ILPSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            request = kwargs['context']['request']
            geometry = request.GET.get('geometry', 'no')
            print("Geometry is: ", geometry)
            # add geometry to fields if geometry=yes in query params
            if geometry == 'yes':
                print("Geometry is YES")
                self.fields['geometry'] = DictField(source='get_geometry')

    

class ILPSimpleGeoSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(ILPSimpleGeoSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            request = kwargs['context']['request']
            geometry = request.GET.get('geometry', 'no')
            simplify = request.GET.get('simplify', 'yes')

            if geometry == 'yes' and simplify == 'no':
                self.fields['geometry'] = DictField(source='get_geometry')

            if geometry == 'yes' and simplify == 'yes':
                self.fields['geometry'] = \
                    DictField(source='get_simple_geometry')


class InstitutionTypeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='char_id')

    class Meta:
        model = InstitutionType
        fields = ['id', 'name']


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ['char_id', 'name']
