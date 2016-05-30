from rest_framework import permissions


class HasStaffAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.access.is_staff
