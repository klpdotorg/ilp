from rest_framework import permissions


class IsAdminOrIsSelf(permissions.BasePermission):
    '''
        Permission class for user profile editing funcs
        Checks whether user is superuser or the same user as being edited
    '''

    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_superuser
