from ..user.authorization import office_auth, owner_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^companies$', login_required(views.CompanyList.as_view()), name='companies'),
    url(r'^create-company$', office_auth(views.CompanyCreate.as_view()), name='company.create'),
    url(r'^company-(?P<pk>.*?)/edit$', office_auth(views.CompanyUpdate.as_view()), name='company.edit'),
    url(r'^company-(?P<pk>.*?)/delete$', office_auth(views.CompanyDelete.as_view()), name='company.delete'),

]
