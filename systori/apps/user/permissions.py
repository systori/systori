from rest_framework import permissions
from systori.apps.company.models import Worker


class WorkerIsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        try:
            worker = request.worker
        except AttributeError:
            worker = None
        if not worker and is_authenticated:
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
    Manage projects and perform administrative tasks.
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_staff


class HasLaborerAccess(WorkerIsAuthenticated):
    """
    Limited access in the field.
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_laborer


class HasForemanAccess(WorkerIsAuthenticated):
    """
    Manage workers in the field.
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_foreman


class HasOwnerAccess(WorkerIsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.has_owner


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.worker.user == request.user


class CanTrackTime(WorkerIsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.worker.can_track_time
