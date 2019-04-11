from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from systori.apps.company.views import (
    CompanyList,
    CompanyCreate,
    CompanyUpdate,
    CompanyDelete,
)

urlpatterns = [
    url(r"^companies$", login_required(CompanyList.as_view()), name="companies"),
    url(
        r"^create-company$",
        login_required(CompanyCreate.as_view()),
        name="company.create",
    ),
    url(
        r"^company-(?P<pk>.*?)/edit$",
        login_required(CompanyUpdate.as_view()),
        name="company.edit",
    ),
    url(
        r"^company-(?P<pk>.*?)/delete$",
        login_required(CompanyDelete.as_view()),
        name="company.delete",
    ),
]
