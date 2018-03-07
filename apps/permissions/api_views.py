from rest_framework import permissions

class BasicDefaultPermission(permissions.BasePermission):
    """
        Global permission check to ensure that only GET, HEAD and POST
        are allowed to ilp_auth_user and everything else is disabled
    """
    def has_permission(self, request, view):
        user = request.user
        print("user is: ", user.first_name)
        user.groups.filter(name='ilp_auth_user').exists()
        if request.user.is_authenticated and request.method in ('POST', 'GET', 'OPTIONS'):
            print("User is authenticated.PERMIT POST, GET AND HEAD")
            return True
        else:
            print("User is anonymous. PERMIT GET AND HEAD")
        return False