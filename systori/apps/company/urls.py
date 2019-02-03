from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from . import views, api

urlpatterns = [
    url(r"^companies$", login_required(views.CompanyList.as_view()), name="companies"),
    url(r"^api/companies/$", api.CompanyApiView.as_view({'get': 'retrieve'}), name="api.companies"),
    url(
        r"^create-company$",
        login_required(views.CompanyCreate.as_view()),
        name="company.create",
    ),
    url(
        r"^company-(?P<pk>.*?)/edit$",
        login_required(views.CompanyUpdate.as_view()),
        name="company.edit",
    ),
    url(
        r"^company-(?P<pk>.*?)/delete$",
        login_required(views.CompanyDelete.as_view()),
        name="company.delete",
    ),
]
