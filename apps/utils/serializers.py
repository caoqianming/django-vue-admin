
from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from rest_framework.fields import empty
from rest_framework.request import Request

class BaseSerizlierMixin:
    create_by_name = serializers.CharField(source='create_by.name', read_only=True)
    update_by_name = serializers.CharField(source='update_by.name', read_only=True)

class PkSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(max_length=20), label="主键ID列表")
    soft = serializers.BooleanField(
        label="是否软删除", default=True, required=False)


class GenSignatureSerializer(serializers.Serializer):
    path = serializers.CharField(label="图片地址")


class CustomModelSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    自定义serializer/包含创建和新增字段处理
    """

    def __init__(self, instance=None, data=empty, request=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.request: Request = request or self.context.get('request', None)

    def create(self, validated_data):
        if self.request:
            if getattr(self.request, 'user', None):
                if getattr(self.Meta.model, 'create_by', None):
                    validated_data['create_by'] = self.request.user
                    validated_data['update_by'] = self.request.user
                    if 'belong_dept' in validated_data:
                        pass
                    elif getattr(self.request.user, 'belong_dept', None):
                        if hasattr(self.Meta.model, 'belong_dept'):
                            validated_data['belong_dept'] = self.request.user.belong_dept
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if self.request:
            if hasattr(instance, 'update_by'):
                validated_data['update_by'] = getattr(
                    self.request, 'user', None)
        return super().update(instance, validated_data)


class QuerySerializer(serializers.Serializer):
    field = serializers.CharField(label='字段名')
    compare = serializers.ChoiceField(
        label='比较式', choices=["", "!", "gte", "gt", "lte", "lt", "in", "contains"])
    value = serializers.CharField(label='值')


class ComplexSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=0, required=False)
    page_size = serializers.IntegerField(min_value=1, required=False)
    querys = serializers.ListField(child=QuerySerializer(
        many=True), label="查询列表", required=False)
