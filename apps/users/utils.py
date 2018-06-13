from rest_framework.authtoken.models import Token


def login_user(request, user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


def logout_user(request):
    Token.objects.filter(user=request.user).delete()


def check_source_and_add_user_to_group(user):
    """
        Checks user's mobile number and PreGroupUser 
    """
    pass
