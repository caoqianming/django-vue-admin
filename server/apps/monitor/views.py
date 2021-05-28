from django.shortcuts import render
import psutil
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.conf import settings
import os
from rest_framework import serializers, status
# Create your views here.

class ServerInfoView(APIView):
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

class LogView(APIView):
    
    def get(self, request, *args, **kwargs):
        """
        查看最近的日志列表
        """
        logs =[]   
        for root, dirs, files in os.walk(settings.LOG_PATH):
            for file in files:
                if len(logs)>50:break
                filepath = os.path.join(root, file)
                fsize = os.path.getsize(filepath)
                if fsize:
                    logs.append({
                        "name":file,
                        "filepath":filepath,
                        "size":round(fsize/1000,1)
                    })
        return Response(logs)
    
class LogDetailView(APIView):

    def get(self, request, name):
        """
        查看日志详情
        """
        try:
            with open(os.path.join(settings.LOG_PATH, name)) as f:
                data = f.read()
            return Response(data)
        except:
            return Response('未找到', status=status.HTTP_404_NOT_FOUND)