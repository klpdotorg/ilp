from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()


class EmailMobileUsernameBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(
                Q(email__iexact=username) | Q(mobile_no__iexact=username))
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid email or mobile number')

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class PasswordlessAuthenticationBackend(object):
    def authenticate(self, uid):
        print('uid', uid)
        if not User.objects.filter(sms_pin=uid).exists():
            print('no token found')
            return None
        try:
            user = User.objects.get(sms_pin=uid)
            print('got user')
            return user
        except User.DoesNotExist:
            print('new user', file=sys.stderr)


    def get_user(self, uid):
        return User.objects.get(sms_pin=uid)