class DartiumCheckMiddleware(object):

    def process_request(self, request):
        request.is_dartium = False
        if 'HTTP_USER_AGENT' in request.META :
            user_agent = request.META['HTTP_USER_AGENT']
            if user_agent and '(Dart)' in user_agent:
                request.is_dartium = True
