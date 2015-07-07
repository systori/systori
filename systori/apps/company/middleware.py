from .models import Access


class AccessMiddleware:

    def process_view(self, request, view, args, kwargs):
        if request.user.is_authenticated() and request.company:
            request.access = Access.objects.get(user=request.user, company=request.company)
        else:
            request.access = None

    def process_template_response(self, request, response):
        response.context_data['access'] = request.access
        return response
