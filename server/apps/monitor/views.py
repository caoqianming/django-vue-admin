from django.shortcuts import render
import psutil
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.conf import settings
import os
from rest_framework import serializers, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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

def get_file_list(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list,key=lambda x: os.path.getmtime(os.path.join(file_path, x)), reverse=True)
        # print(dir_list)
        return dir_list
        
class LogView(APIView):
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('name', openapi.IN_QUERY, description='日志文件名', type=openapi.TYPE_STRING)
    ])
    def get(self, request, *args, **kwargs):
        """
        查看最近的日志列表
        :query name
        """
        logs =[]
        name = request.GET.get('name', None)
        # for root, dirs, files in os.walk(settings.LOG_PATH):
        #     files.reverse()
        for file in get_file_list(settings.LOG_PATH):
            if len(logs)>50:break
            filepath = os.path.join(settings.LOG_PATH, file)
            if name:
                if name in filepath:
                    fsize = os.path.getsize(filepath)
                    if fsize:
                            logs.append({
                                "name":file,
                                "filepath":filepath,
                                "size":round(fsize/1000,1)
                            })
            else:
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