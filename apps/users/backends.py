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
            print("user is: ", user)
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
