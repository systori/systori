from rest_framework import permissions


class HasStaffAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_staff


class HasLaborerAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have laborer access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_laborer
