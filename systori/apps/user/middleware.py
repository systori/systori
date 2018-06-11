from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import check_for_language, LANGUAGE_SESSION_KEY


class SetLanguageMiddleware(MiddlewareMixin):
    """
    Set user language to what's stored in User.language field.
    Should be placed in MIDDLEWARE_CLASSES:
    - before django's LocaleMiddleware
    - after django's AuthenticationMiddleware

    Also will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language when HTTP_ACCEPT_LANGUAGE is set to english.
    Rationale is that not everyone knows how to set this setting correctly in
    their browser so we default to German.
    """

    def process_request(self, request):
        if request.META.get("HTTP_ACCEPT_LANGUAGE", "").startswith("en"):
            del request.META["HTTP_ACCEPT_LANGUAGE"]

        if request.user.is_authenticated:
            user = request.user
            if user.language and check_for_language(user.language):
                request.session[LANGUAGE_SESSION_KEY] = user.language
