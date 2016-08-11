from django.conf.urls import url
from ..user.authorization import office_auth
from .views import *

urlpatterns = [
    url(r'^equipment$', office_auth(EquipmentListView.as_view()), name='equipment.list'),
    url(r'^equipment-(?P<pk>\d+)$', office_auth(EquipmentView.as_view()), name='equipment.view'),
    url(r'^equipment-create$', office_auth(EquipmentCreate.as_view()), name='equipment.create'),
    url(r'^equipment-(?P<pk>\d+)/edit$', office_auth(EquipmentUpdate.as_view()), name='equipment.edit'),
    url(r'^equipment-(?P<pk>\d+)/delete$', office_auth(EquipmentDelete.as_view()), name='equipment.delete'),

    url(r'^equipment-(?P<pk>\d+)/add-refueling-stop$',
        office_auth(RefuelingStopCreate.as_view()), name='refueling_stop.create'),
    url(r'^equipment-(?P<equipment_pk>\d+)/refueling-stop-(?P<pk>\d+)/update$',
        office_auth(RefuelingStopUpdate.as_view()), name='refueling_stop.update'),

    url(r'^equipment-(?P<pk>\d+)/add-defect$',
        office_auth(DefectCreate.as_view()), name='defect.create'),
]
