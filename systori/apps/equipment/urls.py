from django.conf.urls import url
from ..user.authorization import office_auth
from .views import *

urlpatterns = [
    # two url rules to make the active_filter keyword optional
    url(r'^equipment/$', office_auth(EquipmentListView.as_view()), name='equipment.list'),
    url(r'^equipment/(?P<active_filter>[\w-]+)$', office_auth(EquipmentListView.as_view()), name='equipment.list'),
    url(r'^equipment-(?P<pk>\d+)$', office_auth(EquipmentView.as_view()), name='equipment.view'),
    url(r'^create-equipment$', office_auth(EquipmentCreate.as_view()), name='equipment.create'),
    url(r'^equipment-(?P<pk>\d+)/edit$', office_auth(EquipmentUpdate.as_view()), name='equipment.edit'),
    url(r'^equipment-(?P<pk>\d+)/delete$', office_auth(EquipmentDelete.as_view()), name='equipment.delete'),

    url(r'^equipment-(?P<pk>\d+)/create-refueling-stop$',
        office_auth(RefuelingStopCreate.as_view()), name='refueling_stop.create'),
    url(r'^equipment-(?P<equipment_pk>\d+)/refueling-stop-(?P<pk>\d+)/update$',
        office_auth(RefuelingStopUpdate.as_view()), name='refueling_stop.update'),
    url(r'^equipment-(?P<equipment_pk>\d+)/refueling-stop-(?P<pk>\d+)/delete',
        office_auth(RefuelingStopDelete.as_view()), name='refueling_stop.delete'),

    url(r'^equipment-(?P<pk>\d+)/create-maintenance',
        office_auth(MaintenanceCreate.as_view()), name='maintenance.create'),
    url(r'^equipment-(?P<equipment_pk>\d+)/maintenance-(?P<pk>\d+)/update$',
        office_auth(MaintenanceUpdate.as_view()), name='maintenance.update'),
    url(r'^equipment-(?P<equipment_pk>\d+)/maintenance-(?P<pk>\d+)/delete',
        office_auth(MaintenanceDelete.as_view()), name='maintenance.delete'),
]
