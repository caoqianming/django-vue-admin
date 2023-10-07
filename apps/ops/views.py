
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import os
from apps.ops.serializers import DbbackupDeleteSerializer, MemDiskSerializer, CpuSerializer, DrfRequestLogSerializer, TlogSerializer, TextListSerializer
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from apps.ops.filters import DrfLogFilterSet, TlogFilterSet
from apps.ops.models import DrfRequestLog, Tlog

from apps.ops.errors import LOG_NOT_FONED
from apps.utils.viewsets import CustomGenericViewSet
from rest_framework.exceptions import APIException
from apps.ops.tasks import reload_server_git, reload_server_only, reload_web_git, backup_database, backup_media
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from apps.ops.service import ServerService
from server.settings import BACKUP_PATH
# Create your views here.


def index(request):
    return render(request, 'ops/index.html')


def room(request, room_name):
    return render(request, 'ops/room.html', {
        'room_name': room_name
    })


class ReloadServerGit(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(operation_summary="拉取后端代码并重启服务", responses=None, request_body=None)
    def post(self, request):
        reload_server_git.delay()
        return Response()
        # if completed.returncode == 0:
        #     return Response()
        # else:
        #     from server.settings import myLogger
        #     myLogger.error(completed)
        #     raise ParseError(completed.stderr)


class ReloadClientGit(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(operation_summary="拉取前端代码并打包", responses=None, request_body=None)
    def post(self, request):
        reload_web_git.delay()
        return Response()
        # completed = reload_web_git()
        # if completed.returncode == 0:
        #     return Response()
        # else:
        #     raise APIException(completed.stdout)


class ReloadServerOnly(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(operation_summary="仅重启服务", responses=None, request_body=None)
    def post(self, request):
        completed = reload_server_only()
        if completed.returncode == 0:
            return Response()
        else:
            raise APIException(completed.stdout)


class BackupDatabase(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(operation_summary="备份数据库到指定位置", responses=None, request_body=None)
    def post(self, request):
        err_str = backup_database()
        if err_str:
            raise APIException(err_str)
        return Response()


class BackupMedia(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(operation_summary="备份资源到指定位置", responses=None, request_body=None)
    def post(self, request):
        err_str = backup_media()
        if err_str:
            raise APIException(err_str)
        return Response()


class CpuView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="获取服务器cpu当前状态", responses=CpuSerializer, request_body=None)
    def get(self, request, *args, **kwargs):
        return Response(ServerService.get_cpu_dict())


class MemoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="获取服务器内存当前状态", responses=MemDiskSerializer, request_body=None)
    def get(self, request, *args, **kwargs):
        return Response(ServerService.get_memory_dict())


class DiskView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="获取服务器硬盘当前状态", responses=MemDiskSerializer, request_body=None)
    def get(self, request, *args, **kwargs):
        return Response(ServerService.get_disk_dict())


def get_file_list(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(
            os.path.join(file_path, x)), reverse=True)
        # print(dir_list)
        return dir_list


class LogView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="查看最近的日志列表", responses=TextListSerializer(many=True), request_body=None)
    def get(self, request, *args, **kwargs):
        logs = []
        name = request.GET.get('name', None)
        # for root, dirs, files in os.walk(settings.LOG_PATH):
        #     files.reverse()
        for file in get_file_list(settings.LOG_PATH):
            if len(logs) > 50:
                break
            filepath = os.path.join(settings.LOG_PATH, file)
            if name:
                if name in filepath:
                    fsize = os.path.getsize(filepath)
                    if fsize:
                        logs.append({
                            "name": file,
                            "filepath": filepath,
                            "size": round(fsize/1024, 1)
                        })
            else:
                fsize = os.path.getsize(filepath)
                if fsize:
                    logs.append({
                        "name": file,
                        "filepath": filepath,
                        "size": round(fsize/1024, 1)
                    })
        return Response(logs)


class LogDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="查看日志详情", responses=None)
    def get(self, request, name):
        try:
            with open(os.path.join(settings.LOG_PATH, name)) as f:
                data = f.read()
            return Response(data)
        except Exception:
            raise NotFound(**LOG_NOT_FONED)


class DbBackupDeleteView(APIView):
    perms_map = {'delete': 'dbback.delete'}

    @swagger_auto_schema(operation_summary="删除备份", responses={204: None})
    def delete(self, request, filepath):
        if BACKUP_PATH in filepath:
            os.remove(filepath)
        return Response()


class DbBackupView(APIView):
    perms_map = {'get': '*', 'post': 'dbback.delete'}

    @swagger_auto_schema(operation_summary="批量删除备份", responses={204: None}, request_body=DbbackupDeleteSerializer)
    def post(self, request):
        filepaths = request.data.get('filepaths', [])
        for i in filepaths:
            if BACKUP_PATH in i:
                os.remove(i)
        return Response()

    @swagger_auto_schema(operation_summary="查看最近的备份列表", responses=TextListSerializer(many=True), request_body=None)
    def get(self, request, *args, **kwargs):
        items = []
        name = request.GET.get('name', None)
        backpath = settings.BACKUP_PATH + '/database'
        for file in get_file_list(backpath):
            if len(items) > 50:
                break
            filepath = os.path.join(backpath, file)
            if name:
                if name in filepath:
                    fsize = os.path.getsize(filepath)
                    if fsize:
                        items.append({
                            "name": file,
                            "filepath": filepath,
                            "size": round(fsize/1024/1024, 1)
                        })
            else:
                fsize = os.path.getsize(filepath)
                if fsize:
                    items.append({
                        "name": file,
                        "filepath": filepath,
                        "size": round(fsize/1024/1024, 1)
                    })
        return Response(items)


class DrfRequestLogViewSet(ListModelMixin, CustomGenericViewSet):
    """list:请求日志

    请求日志
    """
    perms_map = {'get': '*'}
    queryset = DrfRequestLog.objects.all()
    list_serializer_class = DrfRequestLogSerializer
    ordering = ['-requested_at']
    filterset_class = DrfLogFilterSet
    search_fields = ['path', 'view']


class TlogViewSet(ListModelMixin, CustomGenericViewSet):
    """list:三方日志查看

    三方日志查看
    """
    perms_map = {'get': '*'}
    queryset = Tlog.objects.all()
    list_serializer_class = TlogSerializer
    ordering = ['-requested_at']
    filterset_class = TlogFilterSet
    search_fields = ['path']
