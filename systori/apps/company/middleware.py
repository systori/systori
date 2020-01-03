import string
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from django.conf import settings
from .models import Company, Worker

SCHEMA_ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + "-")


def get_subdomain(request):
    host = request.META["HTTP_HOST"].split(":")[0]
    assert host.endswith(
        settings.SERVER_NAME
    )  # if this fails, SERVER_NAME needs to be configured in settings
    subdomain = host[: -len(settings.SERVER_NAME)]
    if subdomain and subdomain.endswith("."):
        subdomain = subdomain[:-1]
    return subdomain


class CompanyMiddleware(MiddlewareMixin):
    @staticmethod
    def get_android_development_company(request):
        # Only allow in DEBUG mode
        if not settings.DEBUG:
            return None

        is_android_development = (
            request.META["HTTP_HOST"] == settings.ANDROID_LOCALHOST_LOOPBACK
            and settings.API_DEFAULT_COMPANY
        )

        # Only if android development is setup
        if not is_android_development:
            return None

        try:
            company = Company.objects.get(schema=settings.API_DEFAULT_COMPANY)
        except Company.DoesNotExist:
            pass
        else:
            if company.is_active:
                company.activate()
                return company
        # When nothing found or company is not active
        return None

    @staticmethod
    def process_request(request):

        request.company = None

        android_dev_company = CompanyMiddleware.get_android_development_company(request)
        if android_dev_company:
            request.company = android_dev_company
            return

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

        if request.user.is_authenticated:

            companies = request.user.companies.active()
            if len(companies) == 1:
                company_url = companies[0].url(request)
                return HttpResponseRedirect(company_url)

    @staticmethod
    def process_template_response(request, response):
        if response.context_data is not None:
            response.context_data["selected_company"] = request.company
            current = request.company.schema if request.company else ""
            response.context_data["available_companies"] = []
            if request.user.is_authenticated:
                response.context_data["available_companies"] = [
                    {
                        "name": c.name,
                        "schema": c.schema,
                        "url": c.url(request),
                        "current": c.schema == current,
                    }
                    for c in request.user.companies.active()
                ]
        return response


class WorkerMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        request.worker = None
        if request.user.is_authenticated and request.company:
            try:
                request.worker = Worker.objects.select_related("user").get(
                    user=request.user, company=request.company
                )
            except Worker.DoesNotExist:
                if request.user.is_superuser:
                    request.worker = Worker.grant_superuser_access(
                        request.user, request.company
                    )

    @staticmethod
    def process_template_response(request, response):
        if response.context_data is not None:
            response.context_data["worker"] = request.worker
        return response
