from django.http import HttpResponseRedirect
from django.conf import settings
from .models import Access, Company
import string

SCHEMA_ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + '-')


def get_subdomain(request):
    host = request.META['HTTP_HOST'].split(':')[0]
    assert host.endswith(settings.SERVER_NAME)  # if this fails, SERVER_NAME needs to be configured in settings
    subdomain = host[:-len(settings.SERVER_NAME)]
    if subdomain and subdomain.endswith('.'):
        subdomain = subdomain[:-1]
    return subdomain


class CompanyMiddleware:

    def process_request(self, request):

        request.company = None

        subdomain = get_subdomain(request)

        subdomain_is_safe = set(subdomain) <= SCHEMA_ALLOWED_CHARS

        if subdomain_is_safe:

            try:
                company = Company.objects.get(schema=subdomain)
            except Company.DoesNotExist:
                pass
            else:
                if company.is_active:
                    company.activate()
                    request.company = company
                    return

        if request.user.is_authenticated():

            companies = request.user.visible_companies
            if len(companies) == 1:
                company_url = companies[0].url(request)
                return HttpResponseRedirect(company_url)

    def process_template_response(self, request, response):
        if response.context_data is not None:
            response.context_data['selected_company'] = request.company
            current = request.company.schema if request.company else ''
            response.context_data['available_companies'] = [
                {'name': c.name, 'schema': c.schema, 'url': c.url(request), 'current': c.schema == current}
                for c in request.user.visible_companies
            ]
        return response


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
