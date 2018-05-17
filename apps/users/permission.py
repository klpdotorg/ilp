from rest_framework import permissions


class IsAdminOrIsSelf(permissions.BasePermission):
    '''
        Permission class for user profile editing funcs
        Checks whether user is superuser or the same user as being edited
    '''

    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_superuser


class IsAdminUser(permissions.IsAdminUser):

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        # TODO: IMPROVE ME
        # Somehow the below code is not working.
        #
        # return super(
        #     permissions.IsAdminUser, self
        # ).has_permission(request, view)
        #
        # So using manual check
        return request.user.is_authenticated() and request.user.is_superuser
