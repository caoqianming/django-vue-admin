from django.urls import path
from apps.ops.views import (DrfRequestLogViewSet, CpuView, MemoryView, DiskView, DbBackupDeleteView,
                            LogView, LogDetailView,
                            DbBackupView, ReloadClientGit, ReloadServerGit, ReloadServerOnly,
                            BackupDatabase, BackupMedia, TlogViewSet)

API_BASE_URL = 'api/ops/'
HTML_BASE_URL = 'ops/'
urlpatterns = [
    path(API_BASE_URL + 'reload_server_git/', ReloadServerGit.as_view()),
    path(API_BASE_URL + 'reload_web_git/', ReloadClientGit.as_view()),
    path(API_BASE_URL + 'reload_server_only/', ReloadServerOnly.as_view()),
    path(API_BASE_URL + 'backup_database/', BackupDatabase.as_view()),
    path(API_BASE_URL + 'backup_media/', BackupMedia.as_view()),
    path(API_BASE_URL + 'log/', LogView.as_view()),
    path(API_BASE_URL + 'log/<str:name>/', LogDetailView.as_view()),
    path(API_BASE_URL + 'dbbackup/', DbBackupView.as_view()),
    path(API_BASE_URL + 'dbbackup/<str:filepath>/', DbBackupDeleteView.as_view()),
    path(API_BASE_URL + 'server/cpu/', CpuView.as_view()),
    path(API_BASE_URL + 'server/memory/', MemoryView.as_view()),
    path(API_BASE_URL + 'server/disk/', DiskView.as_view()),
    path(API_BASE_URL + 'request_log/',
         DrfRequestLogViewSet.as_view({'get': 'list'}), name='requestlog_view'),
    path(API_BASE_URL + 'tlog/',
         TlogViewSet.as_view({'get': 'list'}), name='tlog_view'),
]
