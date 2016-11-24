from rest_framework import viewsets, mixins
from rest_framework.routers import DefaultRouter
from .models import Group, Task, LineItem
from .serializers import GroupSerializer, TaskSerializer, LineItemSerializer
from .permissions import HasStaffAccess


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = []#[HasStaffAccess]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = []#[HasStaffAccess]


class LineItemViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
    permission_classes = []#[HasStaffAccess]


router = DefaultRouter()
router.register(r'group', GroupViewSet)
router.register(r'task', TaskViewSet)
router.register(r'lineitem', LineItemViewSet)
urlpatterns = router.urls
