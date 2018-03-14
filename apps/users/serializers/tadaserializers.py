from rest_framework import serializers

from users.models import User

class TadaUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        exclude = (
            'is_email_verified',
            'email_verification_code',
        )
        model = User
    
    def create(self, validated_data):
        groups = validated_data.pop('groups')
        user = User.objects.create(**validated_data)
        for group_name in groups:
            group_obj = Group.objects.get(name=group_name)
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
        if user.is_superuser:
            groups = ['tada_admin']
        return groups