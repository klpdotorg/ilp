from rest_framework import serializers

from users.models import User

class TadaUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    groups = serializers.SerializerMethodField()

    class Meta:
        exclude = (
            'is_email_verified',
            'email_verification_code',
        )
        model = User
    
    def create(self, validated_data):
        print("Validated data is: ", validated_data)
        user = User.objects.create(**validated_data)
        user.is_active=True
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.content = validated_data.get('content', instance.content)
        instance.created = validated_data.get('created', instance.created)
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