from email.mime import base
from django.urls import path, include
from .views import ApkViewSet, FileViewSet, PTaskViewSet, PTaskResultViewSet, PostRoleViewSet, TaskList, \
                    UserPostViewSet, UserViewSet, DeptViewSet, \
                    PermissionViewSet, RoleViewSet, PostViewSet, \
                    DictTypeViewSet, DictViewSet, SysConfigView, SysBaseConfigView, MyScheduleViewSet
from rest_framework import routers

API_BASE_URL = 'api/system/'
HTML_BASE_URL = 'system/'

router = routers.DefaultRouter()
router.register('user', UserViewSet, basename="user")
router.register('dept', DeptViewSet, basename="dept")
router.register('permission', PermissionViewSet, basename="permission")
router.register('role', RoleViewSet, basename="role")
router.register('post', PostViewSet, basename="post")
router.register('dicttype', DictTypeViewSet, basename="dicttype")
router.register('dict', DictViewSet, basename="dict")
router.register('ptask', PTaskViewSet, basename="ptask")
router.register('ptask_result', PTaskResultViewSet, basename="ptask_result")
# router.register('qschedule', QScheduleViewSet, basename="qschedule")
# router.register('qtask_result', QTaskResultViewSet, basename="qtask_result")
router.register('user_post', UserPostViewSet, basename='user_post')
router.register('post_role', PostRoleViewSet, basename='post_role')
router.register('apk', ApkViewSet, basename='apk')
router.register('myschedule', MyScheduleViewSet, basename='myschedule')

router2 = routers.DefaultRouter()
router2.register('file', FileViewSet, basename='file')

urlpatterns = [
    path(API_BASE_URL, include(router.urls)),
    path(API_BASE_URL + 'task/', TaskList.as_view()),
    path(API_BASE_URL + 'base_config/', SysBaseConfigView.as_view()),
    path(API_BASE_URL + 'config/', SysConfigView.as_view()),
    path('api/', include(router2.urls)),
]
