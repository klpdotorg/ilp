from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    is_mobile_verified = serializers.BooleanField(read_only=True)
    groups = serializers.SerializerMethodField()

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
        groups = user.groups.all().values('name')
        if user.is_superuser:
            groups = ['tada_admin']
        return groups


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    groups = serializers.SerializerMethodField()

    class Meta:
        exclude = (
            'is_active',
            'is_staff',
            'is_superuser',
            'is_email_verified',
            'is_mobile_verified',
            'email_verification_code',
            'sms_verification_pin',
        )
        model = User

    def get_groups(self, obj):
        user = obj
        groups = user.groups.all().values('name')
        if user.is_superuser:
            groups = ['tada_admin']
        return groups


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(style={'input_type': 'password'})
    password = serializers.CharField(style={'input_type': 'password'})
    groups = serializers.SerializerMethodField()

    class Meta:
        fields = ('username', 'password', )

    def get_groups(self, obj):
        user = obj
        groups = user.groups.all().values('name')
        print("Groups the user is a part of: ", groups)
        if user.is_superuser:
            groups = ['tada_admin']
        return groups

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(
            username=attrs.get('username'),
            password=attrs.get('password')
        )
        self._validate_user_exists(self.user)
        self._validate_user_is_active(self.user)
        return attrs

    def _validate_user_exists(self, user):
        if not user:
            raise serializers.ValidationError('Invalid username/password')

    def _validate_user_is_active(self, user):
        if not user.is_active:
            raise serializers.ValidationError('User account is inactive')


class OtpSerializer(serializers.Serializer):
    mobile_no = serializers.CharField()
    otp = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        fields = ('mobile_no', 'otp', )


class OtpGenerateSerializer(serializers.Serializer):
    mobile_no = serializers.CharField()

    class Meta:
        fields = ('mobile_no', )


class OtpPasswordResetSerializer(serializers.Serializer):
    mobile_no = serializers.CharField()
    otp = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        fields = ('mobile_no', 'otp', 'password', )
