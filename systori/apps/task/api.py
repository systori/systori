from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from .models import Group, Task
from .serializers import GroupSerializer, TaskSerializer
from .permissions import HasStaffAccess


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [HasStaffAccess]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [HasStaffAccess]


router = DefaultRouter()
router.register(r'group', GroupViewSet)
router.register(r'task', TaskViewSet)
urlpatterns = router.urls
