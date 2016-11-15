from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from .models import Group
from .serializers import GroupSerializer
from .permissions import HasStaffAccess


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [HasStaffAccess]


router = DefaultRouter()
router.register(r'group', GroupViewSet)
urlpatterns = router.urls
