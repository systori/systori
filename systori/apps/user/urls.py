from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from rest_framework.authtoken import views as drf_views
from . import views

urlpatterns = [
    url(r"^accounts/", include("allauth.urls")),
    url(r"api/token/", drf_views.obtain_auth_token, name="drf.tokenauth"),
    url(r"^settings$", login_required(views.SettingsView.as_view()), name="settings"),
    url(r"^set_language$", views.SetLanguageView.as_view(), name="set_language"),
    url(r"^users$", office_auth(views.WorkerList.as_view()), name="users"),
    url(r"^add-user$", office_auth(views.UserAdd.as_view()), name="user.add"),
    url(r"^user-(?P<pk>\d+)$", office_auth(views.UserView.as_view()), name="user.view"),
    url(
        r"^user-(?P<pk>\d+)/edit$",
        office_auth(views.UserUpdate.as_view()),
        name="user.edit",
    ),
    url(
        r"^access-(?P<pk>\d+)/remove$",
        office_auth(views.WorkerRemove.as_view()),
        name="access.remove",
    ),
    url(
        r"^user-(?P<pk>\d+)/generate-password$",
        office_auth(views.UserGeneratePassword.as_view()),
        name="user.generate.password",
    ),
]
