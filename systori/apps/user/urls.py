from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views import *

urlpatterns = [

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'user/login.html'}, name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    url(r'^settings$', login_required(SettingsView.as_view()), name='settings'),

    url(r'^users$', office_auth(UserList.as_view()), name='users'),

    url(r'^add-user$', office_auth(UserAdd.as_view()), name='user.add'),
    url(r'^user-(?P<pk>\d+)$', office_auth(UserView.as_view()), name='user.view'),
    url(r'^user-(?P<pk>\d+)/edit$', office_auth(UserUpdate.as_view()), name='user.edit'),
    url(r'^user-(?P<pk>\d+)/remove$', office_auth(UserRemove.as_view()), name='user.remove'),
]
