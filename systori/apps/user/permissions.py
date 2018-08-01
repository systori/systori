from rest_framework import permissions
from systori.apps.company.models import Worker

class HasStaffAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        worker = Worker.objects.get(user=request.user)
        return is_authenticated and worker.has_staff


class HasLaborerAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have laborer access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        worker = Worker.objects.get(user=request.user)
        return is_authenticated and worker.has_laborer
