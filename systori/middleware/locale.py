class ForceDefaultLanguageMiddleware(object):
    """
    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language when HTTP_ACCEPT_LANGUAGE is set to english.
    Rationale is that not everyone knows how to set this setting correctly in
    their browser so we default to German.
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            if request.META['HTTP_ACCEPT_LANGUAGE'].find('en') == 0:
                del request.META['HTTP_ACCEPT_LANGUAGE']