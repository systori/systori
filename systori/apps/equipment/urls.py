from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import EquipmentListView
from .views import \
    VehicleListView, VehicleView, VehicleUpdate, VehicleDelete, VehicleCreate


urlpatterns = patterns('',
    url(r'^equipment$',
        office_auth(EquipmentListView.as_view()), name='equipment.list'),

    url(r'^vehicle$',
        office_auth(VehicleListView.as_view()), name='vehicle.list'),
    url(r'^vehicle-(?P<pk>\d+)$',
        office_auth(VehicleView.as_view()), name='vehicle.view'),
    url(r'^vehicle-create$',
        office_auth(VehicleCreate.as_view()), name='vehicle.create'),
    url(r'^vehicle-(?P<pk>\d+)/edit$',
        office_auth(VehicleUpdate.as_view()), name='vehicle.edit'),
    url(r'^vehicle-(?P<pk>\d+)/delete$',
        office_auth(VehicleDelete.as_view()), name='vehicle.delete'),
)
