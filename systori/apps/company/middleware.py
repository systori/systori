from .models import Access


class AccessMiddleware:

    def process_view(self, request, view, args, kwargs):
        request.access = None
        if request.user.is_authenticated() and request.company:
            try:
                request.access = Access.objects.select_related("user").get(user=request.user, company=request.company)
            except Access.DoesNotExist:
                if request.user.is_superuser:
                    request.access = Access.grant_superuser_access(request.user, request.company)

    def process_template_response(self, request, response):
        response.context_data['access'] = request.access
        return response
