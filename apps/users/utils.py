import logging

from rest_framework.authtoken.models import Token

from .models import PreGroupUser
from .serializers import UserSerializer


logger = logging.getLogger(__name__)


def login_user(request, user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


def logout_user(request):
    Token.objects.filter(user=request.user).delete()


def check_source_and_add_user_to_group(request, user):
    """
        Checks user's mobile number and PreGroupUser model to see if the user
        exists there.
        If the user exists, adds the user to corresponding model.
    """
    try:
        pre_group = PreGroupUser.objects.get(
            mobile_no=user.mobile_no,
            source=request.data.get('source', '')
        )
    except PreGroupUser.DoesNotExist:
        logger.debug('User does not belong to any PreGroup')
        return None
    else:
        logger.debug('User belongs to %s' % pre_group.group.name)
        user.groups.add(pre_group.group)
        user.save()
        return pre_group


def activate_user_and_login(request, user, password=None):
    """
        Activates an user and returns the full user object including the token.
        Also resets the password if it is given.
    """
    user.sms_verification_pin = None
    user.is_active = True
    user.is_mobile_verified = True
    if password is not None:
        user.set_password(password)
    user.save()

    data = UserSerializer(user).data
    data['token'] = login_user(request, user).key
    data['success'] = 'ok'
    return data
