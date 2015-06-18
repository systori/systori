from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied


def office_auth(view):
    def is_authorized(user):
        if not user.is_authenticated():
            return False  # redirect to login
        if user.has_staff:
            return True  # all good
        raise PermissionDenied  # logged in but not allowed

    return user_passes_test(is_authorized)(view)


def field_auth(view):
    def is_authorized(user):
        if not user.is_authenticated():
            return False  # redirect to login
        if user.has_laborer:
            return True  # all good
        raise PermissionDenied  # logged in but not allowed

    return user_passes_test(is_authorized)(view)
