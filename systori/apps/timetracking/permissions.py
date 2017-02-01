from rest_framework import permissions


class HasTimetrackingAccess(permissions.IsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        return request.worker.timetracking_enabled


class CanTrackTime(permissions.IsAuthenticated):
    """
    Allows access only users that have staff access
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        return request.worker.can_track_time
