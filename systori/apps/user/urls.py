from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include

from systori.apps.user.api import SystoriAuthToken
from systori.apps.user.authorization import office_auth
from systori.apps.user.views import (
    SettingsView,
    SetLanguageView,
    WorkerList,
    UserAdd,
    UserView,
    UserUpdate,
    WorkerRemove,
    UserGeneratePassword,
)

urlpatterns = [
    url(r"^accounts/", include("allauth.urls")),
    url(r"api/token/", SystoriAuthToken.as_view(), name="drf.tokenauth"),
    url(r"^settings$", login_required(SettingsView.as_view()), name="settings"),
    url(r"^set_language$", SetLanguageView.as_view(), name="set_language"),
    url(r"^users$", office_auth(WorkerList.as_view()), name="users"),
    url(r"^add-user$", office_auth(UserAdd.as_view()), name="user.add"),
    url(r"^user-(?P<pk>\d+)$", office_auth(UserView.as_view()), name="user.view"),
    url(
        r"^user-(?P<pk>\d+)/edit$", office_auth(UserUpdate.as_view()), name="user.edit"
    ),
    url(
        r"^access-(?P<pk>\d+)/remove$",
        office_auth(WorkerRemove.as_view()),
        name="access.remove",
    ),
    url(
        r"^user-(?P<pk>\d+)/generate-password$",
        office_auth(UserGeneratePassword.as_view()),
        name="user.generate.password",
    ),
]
