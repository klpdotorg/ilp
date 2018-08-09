from rest_framework import serializers

from users.models import User, UserBoundary
from boundary.models import BoundaryStateCode
from boundary.serializers import BoundarySerializer
from drf_writable_nested import WritableNestedModelSerializer

class TadaUserBoundarySerializer(serializers.ModelSerializer):
    boundary = BoundarySerializer()
    
    class Meta:
        model = UserBoundary
        fields = ('boundary',)

class TadaUserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    groups = serializers.SerializerMethodField()
    userboundaries = serializers.ListField()

    class Meta:
        # exclude = (
        #     'email_verification_code',
        #     'is_email_verified'
        # )
        fields = (
            'email', 'mobile_no', 'first_name',
            'last_name', 'user_type', 'is_active',
            'groups', 'is_staff', 'is_superuser',
            'dob', 'source', 'created', 'image',
            'about', 'twitter_handle', 'fb_url',
            'website', 'photos_url', 'youtube_url',
            'userboundaries', 'password'
        )
        model = User
    
    def create(self, validated_data):
        print(validated_data)
        state_codes = validated_data.pop('userboundaries')
        user = User.objects.create(**validated_data)
        user.is_active = True
        user.save()
        print("state codes are:", state_codes)   
        for state_code in state_codes:
            state = BoundaryStateCode.objects.get(char_id=state_code)
            userboundary = UserBoundary.objects.create(user=user, boundary=state.boundary)
            user.save()
            userboundary.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        new_boundaries = validated_data.get('userboundaries', [])
        instance.userboundaries.clear()
        existing_boundaries = UserBoundary.objects.filter(user_id=instance.id)
        existing_boundaries.delete()
        for state_code in new_boundaries:
            state = BoundaryStateCode.objects.get(char_id=state_code)
            userboundary = UserBoundary.objects.create(user=instance, boundary=state.boundary)
            userboundary.save()
            instance.userboundaries.add(userboundary)
        instance.save()
        return instance

    def get_groups(self, obj):
        user = obj
        groups = user.groups.all().values('name')
        return groups




class TadaUserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    is_mobile_verified = serializers.BooleanField(read_only=True)
    groups = serializers.SerializerMethodField()
    userboundaries = TadaUserBoundarySerializer(many=True)

    class Meta:
        model = User
        exclude = (
            'password',
            'email_verification_code',
            'sms_verification_pin',
        )
        read_only_fields = (User.USERNAME_FIELD,)

    def get_groups(self, obj):
        user = obj
        groups = user.groups.all().values_list('name', flat=True)
        return groups

class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    new_password = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)