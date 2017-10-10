from django.contrib.auth import authenticate
from rest_framework import exceptions, serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = (User.USERNAME_FIELD,)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        fields = '__all__'
        model = User


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(style={'input_type': 'password'})
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        fields = ('email', 'password', )

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        # TODO: Uncomment the below line once users.User is set
        # as default auth model
        # self.user = authenticate(
        #     email=attrs.get('email'),
        #     password=attrs.get('password')
        # )
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            self.user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            self.user = None
        self._validate_user_exists(self.user)
        self._validate_user_is_active(self.user)
        return attrs

    def _validate_user_exists(self, user):
        if not user:
            raise serializers.ValidationError('invalid email/password')

    def _validate_user_is_active(self, user):
        if not user.is_active:
            raise serializers.ValidationError('user account is inactive')
