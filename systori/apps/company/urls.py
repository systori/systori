from ..user.authorization import office_auth, owner_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^companies$', login_required(views.CompanyList.as_view()), name='companies'),
    url(r'^create-company$', login_required(views.CompanyCreate.as_view()), name='company.create'),
    url(r'^company-(?P<pk>[a-z0-9\-]+)/edit$', owner_auth(views.CompanyUpdate.as_view()), name='company.edit'),
    url(r'^company-(?P<pk>[a-z0-9\-]+)/delete$', owner_auth(views.CompanyDelete.as_view()), name='company.delete'),

]
