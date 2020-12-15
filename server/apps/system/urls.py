from django.urls import path, include
from .views import TaskcodeList, UserViewSet, OrganizationViewSet, PermissionViewSet, RoleViewSet, PositionViewSet, TestView, DictTypeViewSet, DictViewSet, TaskViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register('user', UserViewSet, basename="user")
router.register('organization', OrganizationViewSet, basename="organization")
router.register('permission', PermissionViewSet, basename="permission")
router.register('role', RoleViewSet, basename="role")
router.register('position', PositionViewSet, basename="position")
router.register('dicttype', DictTypeViewSet, basename="dicttype")
router.register('dict', DictViewSet, basename="dict")
router.register('task', TaskViewSet, basename="task")
urlpatterns = [
    path('', include(router.urls)),
    path('taskcode/', TaskcodeList.as_view()),
    path('test/', TestView.as_view())
]
