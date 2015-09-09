from django.utils.translation import check_for_language, LANGUAGE_SESSION_KEY


class SetLanguageMiddleware:
    """
    Set user language to what's stored in User.language field.
    Should be placed in MIDDLEWARE_CLASSES:
    - before django's LocaleMiddleware
    - after django's AuthenticationMiddleware
    """

    def process_request(self, request):
        if request.user.is_authenticated():
            user = request.user
            if user.language and check_for_language(user.language):
                request.session[LANGUAGE_SESSION_KEY] = user.language
