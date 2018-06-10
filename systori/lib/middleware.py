import time
from django.utils.deprecation import MiddlewareMixin


class StatsMiddleware(MiddlewareMixin):
    def process_request(selfs, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        total = time.time() - request.start_time
        print(f'cycle took {total}')
        return response
