from rest_framework import serializers
from apps.ops.models import DrfRequestLog, Tlog

class DbbackupDeleteSerializer(serializers.Serializer):
    filepaths = serializers.ListField(child=serializers.CharField(), label="文件地址列表")

class MemDiskSerializer(serializers.Serializer):
    total = serializers.FloatField(label="总大小(GB)")
    used  = serializers.FloatField(label="已用(GB)")
    percent = serializers.FloatField(label="百分比")

class CpuSerializer(serializers.Serializer):
    count = serializers.IntegerField(label='物理核心数')
    lcount = serializers.IntegerField(label="逻辑核心数")
    percent = serializers.FloatField(label="百分比")


class DrfRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrfRequestLog
        fields = '__all__'

class TlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tlog
        fields = '__all__'

class TextListSerializer(serializers.Serializer):
    name = serializers.CharField()
    filepath = serializers.CharField()
    size = serializers.CharField(label="MB")
