from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from users.models import User

class PasswordlessAuthentication(BaseAuthentication):
    def authenticate(self, request):
        uid = request.GET.get('token')
        if uid is None:
            return None
        try:
            user = User.objects.get(secure_login_token=uid)
            return (user, None)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            print("User does not exist")
            raise exceptions.AuthenticationFailed('No such user')
    
    
    def get_user(self, user_id):
       try:
          return User.objects.get(secure_login_token=user_id)
       except User.DoesNotExist:
          return None
