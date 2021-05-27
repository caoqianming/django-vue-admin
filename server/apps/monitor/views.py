from django.shortcuts import render
import psutil
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import logging

# Create your views here.

class ServerInfo(APIView):
    """
    获取服务器状态信息
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        ret={'cpu':{}, 'memory':{}, 'disk':{}}
        ret['cpu']['count'] = psutil.cpu_count()
        ret['cpu']['lcount'] = psutil.cpu_count(logical=False)
        ret['cpu']['percent'] = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        ret['memory']['total'] = round(memory.total/1024/1024/1024,2)
        ret['memory']['used'] = round(memory.used/1024/1024/1024,2)
        ret['memory']['percent'] = memory.percent
        disk = psutil.disk_usage('/')
        ret['disk']['total'] = round(disk.total/1024/1024/1024,2)
        ret['disk']['used'] = round(disk.used/1024/1024/1024,2)
        ret['disk']['percent'] = disk.percent
        return Response(ret)
