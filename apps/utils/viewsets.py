
from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.system.models import DataFilter, Dept, User
from apps.utils.errors import PKS_ERROR
from apps.utils.mixins import MyLoggingMixin, BulkCreateModelMixin, BulkUpdateModelMixin, BulkDestroyModelMixin
from apps.utils.permission import ALL_PERMS, RbacPermission, get_user_perms_map
from apps.utils.queryset import get_child_queryset2
from apps.utils.serializers import PkSerializer, ComplexSerializer
from rest_framework.throttling import UserRateThrottle
from drf_yasg.utils import swagger_auto_schema
from apps.utils.decorators import idempotent
from django.db import transaction
import json
from rest_framework.generics import get_object_or_404


class CustomGenericViewSet(MyLoggingMixin, GenericViewSet):
    """
    增强的GenericViewSet
    """
    perms_map = {}  # 权限标识
    throttle_classes = [UserRateThrottle]
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    ordering_fields = '__all__'
    ordering = '-create_time'
    create_serializer_class = None
    update_serializer_class = None
    partial_update_serializer_class = None
    list_serializer_class = None
    retrieve_serializer_class = None
    select_related_fields = []
    prefetch_related_fields = []
    permission_classes = [IsAuthenticated & RbacPermission]
    data_filter = False  # 数据权限过滤是否开启(需要RbacPermission)
    data_filter_field = 'belong_dept'
    hash_k = None
    cache_seconds = 5   # 接口缓存时间默认5秒
    filterset_fields = select_related_fields

    def finalize_response(self, request, response, *args, **kwargs):
        if self.hash_k and self.cache_seconds:
            cache.set(self.hash_k, response.data,
                      timeout=self.cache_seconds)  # 将结果存入缓存，设置超时时间
        return super().finalize_response(request, response, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        cache_seconds = getattr(
            self, f"{self.action}_cache_seconds", getattr(self, 'cache_seconds', 0))
        if cache_seconds:
            self.cache_seconds = cache_seconds
            rdata = {}
            rdata['request_method'] = request.method
            rdata['request_path'] = request.path
            rdata['request_data'] = request.data
            rdata['request_query'] = request.query_params.dict()
            rdata['request_userid'] = request.user.id
            self.hash_k = hash(json.dumps(rdata))
            hash_v_e = cache.get(self.hash_k, None)
            if hash_v_e is None:
                cache.set(self.hash_k, 'o', self.cache_seconds)
            elif hash_v_e == 'o':  # 说明请求正在处理
                raise ParseError(f'请求忽略,请{self.cache_seconds}秒后重试')
            elif hash_v_e:
                return Response(hash_v_e)

    def get_serializer_class(self):
        action_serializer_name = f"{self.action}_serializer_class"
        action_serializer_class = getattr(self, action_serializer_name, None)
        if action_serializer_class:
            return action_serializer_class
        return super().get_serializer_class()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.perms_map:
            for k, v in self.perms_map.items():
                if v not in ALL_PERMS and v != '*':
                    ALL_PERMS.append(v)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        if self.data_filter:
            user = self.request.user
            if user.is_superuser:
                return queryset
            user_perms_map = cache.get('perms_' + str(user.id), None)
            if user_perms_map is None:
                user_perms_map = get_user_perms_map(self.request.user)
            if isinstance(user_perms_map, dict):
                if hasattr(self, 'perms_map'):
                    perms_map = self.perms_map
                    action_str = perms_map.get(
                        self.request._request.method.lower(), None)
                    if '*' in perms_map:
                        return queryset
                    elif action_str == '*':
                        return queryset
                    elif action_str in user_perms_map:
                        new_queryset = queryset.none()
                        for dept_id, data_range in user_perms_map[action_str].items():
                            dept = Dept.objects.get(id=dept_id)
                            if data_range == DataFilter.ALL:
                                return queryset
                            elif data_range == DataFilter.SAMELEVE_AND_BELOW:
                                queryset = self.filter_s_a_b(queryset, dept)
                            elif data_range == DataFilter.THISLEVEL_AND_BELOW:
                                queryset = self.filter_t_a_b(queryset, dept)
                            elif data_range == DataFilter.THISLEVEL:
                                queryset = self.filter_t(queryset, dept)
                            elif data_range == DataFilter.MYSELF:
                                queryset = queryset.filter(create_by=user)
                            new_queryset = new_queryset | queryset
                        return new_queryset
                    else:
                        return queryset.none()
        return queryset

    def filter_s_a_b(self, queryset, dept):
        """过滤同级及以下, 可重写
        """
        if hasattr(queryset.model, 'belong_dept'):
            if dept.parent:
                belong_depts = get_child_queryset2(dept.parent)
            else:
                belong_depts = get_child_queryset2(dept)
            whereis = {self.data_filter_field + '__in': belong_depts}
            queryset = queryset.filter(**whereis)
            return queryset
        return queryset.filter(create_by=self.request.user)

    def filter_t_a_b(self, queryset, dept):
        """过滤本级及以下, 可重写
        """
        if hasattr(queryset.model, 'belong_dept'):
            belong_depts = get_child_queryset2(dept)
            whereis = {self.data_filter_field + '__in': belong_depts}
            queryset = queryset.filter(**whereis)
            return queryset
        return queryset.filter(create_by=self.request.user)

    def filter_t(self, queryset, dept):
        """过滤本级, 可重写
        """
        if hasattr(queryset.model, 'belong_dept'):
            whereis = {self.data_filter_field: dept}
            queryset = queryset.filter(whereis)
            return queryset
        return queryset.filter(create_by=self.request.user)


class CustomModelViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, ListModelMixin,
                         RetrieveModelMixin, BulkDestroyModelMixin, CustomGenericViewSet):
    """
    增强的ModelViewSet
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # 增加默认权限标识
        if not self.perms_map or self.perms_map == {'get': '*'}:
            basename = self.basename
            self.perms_map = {'get': '*', 'post': '{}.create'.format(basename), 'put': '{}.update'.format(
                basename), 'patch': '{}.update'.format(basename), 'delete': '{}.delete'.format(basename)}
        for k, v in self.perms_map.items():
            if v not in ALL_PERMS and v != '*':
                ALL_PERMS.append(v)

    @swagger_auto_schema(request_body=ComplexSerializer, responses={200: {}})
    @action(methods=['post'], detail=False, perms_map={'post': '*'})
    def cquery(self, request):
        """复杂查询

        复杂查询
        """
        sr = ComplexSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        queryset = self.filter_queryset(self.get_queryset())
        new_qs = queryset.none()
        try:
            for m in vdata.get('querys', []):
                one_qs = queryset
                for n in m:
                    st = {}
                    if n['compare'] == '!':  # 如果是排除比较式
                        st[n['field']] = n['value']
                        one_qs = one_qs.exclude(**st)
                    elif n['compare'] == '':
                        st[n['field']] = n['value']
                        one_qs = one_qs.filter(**st)
                    else:
                        st[n['field'] + '__' + n['compare']] = n['value']
                        one_qs = one_qs.filter(**st)
                new_qs = new_qs | one_qs
        except Exception as e:
            raise ParseError(str(e))
        page = self.paginate_queryset(new_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(new_qs, many=True)
        return Response(serializer.data)
