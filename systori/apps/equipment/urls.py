from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import EquipmentListView,\
    EquipmentView, EquipmentUpdate, EquipmentDelete, EquipmentCreate


urlpatterns = patterns('',
    url(r'^equipment$',
        office_auth(EquipmentListView.as_view()), name='equipment.list'),
    url(r'^equipment-(?P<pk>\d+)$',
        office_auth(EquipmentView.as_view()), name='equipment.view'),
    url(r'^equipment-create$',
        office_auth(EquipmentCreate.as_view()), name='equipment.create'),
    url(r'^equipment-(?P<pk>\d+)/edit$',
        office_auth(EquipmentUpdate.as_view()), name='equipment.edit'),
    url(r'^equipment-(?P<pk>\d+)/delete$',
        office_auth(EquipmentDelete.as_view()), name='equipment.delete'),
)
