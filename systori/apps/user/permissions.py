from rest_framework import permissions
from systori.apps.company.models import Worker


class WorkerIsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not request.worker:
            try:
                request.worker = Worker.objects.select_related("user").get(
                    user=request.user, company=request.company
                )
            except Worker.DoesNotExist:
                if request.user.is_superuser:
                    request.worker = Worker.grant_superuser_access(
                        request.user, request.company
                    )
        return is_authenticated


class HasStaffAccess(WorkerIsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_staff


class HasLaborerAccess(WorkerIsAuthenticated):
    """
    Allows access only users that have laborer access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_laborer
