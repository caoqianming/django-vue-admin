import uuid
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin
import ast
import ipaddress
import traceback
from apps.ops.models import DrfRequestLog
from django.db import connection
from django.utils.timezone import now
from user_agents import parse
import logging
from rest_framework.response import Response
from django.db import transaction
from rest_framework.exceptions import ParseError, ValidationError
from apps.utils.errors import PKS_ERROR
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.utils.serializers import PkSerializer

# 实例化myLogger
myLogger = logging.getLogger('log')

class CreateUpdateModelAMixin:
    """
    业务用基本表A用
    """

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(update_by=self.request.user)


class CreateUpdateModelBMixin:
    """
    业务用基本表B用
    """

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user, belong_dept=self.request.user.dept)

    def perform_update(self, serializer):
        serializer.save(update_by=self.request.user)


class CreateUpdateCustomMixin:
    """
    整合
    """

    def perform_create(self, serializer):
        if hasattr(self.queryset.model, 'belong_dept'):
            serializer.save(create_by=self.request.user, belong_dept=self.request.user.dept)
        else:
            serializer.save(create_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(update_by=self.request.user)


class CustomCreateModelMixin(CreateModelMixin):

    def perform_create(self, serializer):
        if hasattr(self.queryset.model, 'belong_dept'):
            serializer.save(create_by=self.request.user, belong_dept=self.request.user.dept)
        else:
            serializer.save(create_by=self.request.user)


class CustomUpdateModelMixin(UpdateModelMixin):

    def perform_update(self, serializer):
        serializer.save(update_by=self.request.user)


class BulkCreateModelMixin(CreateModelMixin):

    def after_bulk_create(self, objs):
        pass

    def create(self, request, *args, **kwargs):
        """创建(支持批量)

        创建(支持批量)
        """
        rdata = request.data
        many = False
        if isinstance(rdata, list):
            many = True
        with transaction.atomic():
            sr = self.get_serializer(data=rdata, many=many)
            sr.is_valid(raise_exception=True)
            self.perform_create(sr)
        if many:
            self.after_bulk_create(sr.data)
        return Response(sr.data, status=201)
        

class BulkUpdateModelMixin(UpdateModelMixin):

    def after_bulk_update(self, objs):
        pass
    
    def partial_update(self, request, *args, **kwargs):
        """部分更新(支持批量)

        部分更新(支持批量)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新(支持批量)

        更新(支持批量)
        """
        partial = kwargs.pop('partial', False)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if kwargs[lookup_url_kwarg] == 'bulk':  # 如果是批量操作
            queryset = self.filter_queryset(self.get_queryset())
            objs = []
            if isinstance(request.data, list):
                with transaction.atomic():
                    for ind, item in enumerate(request.data):
                        obj = get_object_or_404(queryset, id=item['id'])
                        sr = self.get_serializer(obj, data=item, partial=partial)
                        if not sr.is_valid():
                            err_dict = { f'第{ind+1}': sr.errors}
                            raise ValidationError(err_dict)
                        self.perform_update(sr)  # 用自带的更新,可能需要做其他操作
                        objs.append(sr.data)
                    self.after_bulk_update(objs)
            else:
                raise ParseError('提交数据非列表')
            return Response(objs)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)


class BulkDestroyModelMixin(DestroyModelMixin):

    @swagger_auto_schema(request_body=PkSerializer)
    def destroy(self, request, *args, **kwargs):
        """删除(支持批量)

        删除(支持批量和硬删除(需管理员权限))
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if kwargs[lookup_url_kwarg] == 'bulk':  # 如果是批量操作
            queryset = self.filter_queryset(self.get_queryset())
            ids = request.data.get('ids', None)
            soft = request.data.get('soft', True)
            if  not soft and not request.user.is_superuser:
                raise ParseError('非管理员不支持物理删除')
            if ids:
                if soft is True:
                    queryset.filter(id__in=ids).delete()
                elif soft is False:
                    try:
                        queryset.model.objects.get_queryset(
                            all=True).filter(id__in=ids).delete(soft=False)
                    except Exception:
                        queryset.filter(id__in=ids).delete()
                return Response(status=204)
            else:
                raise ValidationError(**PKS_ERROR)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
        return Response(status=204)

class CustomListModelMixin(ListModelMixin):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="query", in_=openapi.IN_QUERY, description="定制返回数据",
                          type=openapi.TYPE_STRING, required=False),
    ])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_info_for_list(serializer.data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = self.add_info_for_list(serializer.data)
        return Response(data)

    def add_info_for_list(self, data):
        """给list返回数据添加额外信息

        给list返回数据添加额外信息
        """
        return data

class MyLoggingMixin(object):
    """Mixin to log requests"""

    CLEANED_SUBSTITUTE = "********************"

    # logging_methods = "__all__"
    logging_methods = '__all__'
    sensitive_fields = {}

    def __init__(self, *args, **kwargs):
        assert isinstance(
            self.CLEANED_SUBSTITUTE, str
        ), "CLEANED_SUBSTITUTE must be a string."
        super().__init__(*args, **kwargs)

    def initial(self, request, *args, **kwargs):
        request_id = uuid.uuid4()
        self.log = {"requested_at": now(), "id": request_id}
        setattr(request, 'request_id', request_id)
        if not getattr(self, "decode_request_body", False):
            self.log["data"] = ""
        else:
            self.log["data"] = self._clean_data(request.body)

        super().initial(request, *args, **kwargs)

        try:
            # Accessing request.data *for the first time* parses the request body, which may raise
            # ParseError and UnsupportedMediaType exceptions. It's important not to swallow these,
            # as (depending on implementation details) they may only get raised this once, and
            # DRF logic needs them to be raised by the view for error handling to work correctly.
            data = self.request.data.dict()
        except AttributeError:
            data = self.request.data
        self.log["data"] = self._clean_data(data)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        self.log["errors"] = traceback.format_exc()
        return response

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        # Ensure backward compatibility for those using _should_log hook
        should_log = (
            self._should_log if hasattr(self, "_should_log") else self.should_log
        )
        if should_log(request, response):
            if (connection.settings_dict.get("ATOMIC_REQUESTS") and
                    getattr(response, "exception", None) and connection.in_atomic_block):
                # response with exception (HTTP status like: 401, 404, etc)
                # pointwise disable atomic block for handle log (TransactionManagementError)
                connection.set_rollback(True)
                connection.set_rollback(False)
            if response.streaming:
                rendered_content = None
            elif hasattr(response, "rendered_content"):
                rendered_content = response.rendered_content
            else:
                rendered_content = response.getvalue()

            self.log.update(
                {
                    "remote_addr": self._get_ip_address(request),
                    "view": self._get_view_name(request),
                    "view_method": self._get_view_method(request),
                    "path": self._get_path(request),
                    "host": request.get_host(),
                    "method": request.method,
                    "query_params": self._clean_data(request.query_params.dict()),
                    "user": self._get_user(request),
                    "response_ms": self._get_response_ms(),
                    "response": self._clean_data(rendered_content),
                    "status_code": response.status_code,
                    "agent": self._get_agent(request),
                }
            )
            try:
                self.handle_log()
            except Exception:
                # ensure that all exceptions raised by handle_log
                # doesn't prevent API call to continue as expected
                myLogger.exception("Logging API call raise exception!")
        return response

    def handle_log(self):
        """
        Hook to define what happens with the log.

        Defaults on saving the data on the db.
        """
        DrfRequestLog(**self.log).save()

    def _get_path(self, request):
        """Get the request path and truncate it"""
        return request.path

    def _get_ip_address(self, request):
        """Get the remote ip address the request was generated from."""
        ipaddr = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ipaddr:
            ipaddr = ipaddr.split(",")[0]
        else:
            ipaddr = request.META.get("REMOTE_ADDR", "")

        # Account for IPv4 and IPv6 addresses, each possibly with port appended. Possibilities are:
        # <ipv4 address>
        # <ipv6 address>
        # <ipv4 address>:port
        # [<ipv6 address>]:port
        # Note that ipv6 addresses are colon separated hex numbers
        possibles = (ipaddr.lstrip("[").split("]")[0], ipaddr.split(":")[0])

        for addr in possibles:
            try:
                return str(ipaddress.ip_address(addr))
            except ValueError:
                pass

        return ipaddr

    def _get_view_name(self, request):
        """Get view name."""
        method = request.method.lower()
        try:
            attributes = getattr(self, method)
            return (
                type(attributes.__self__).__module__ + "." + type(attributes.__self__).__name__
            )

        except AttributeError:
            return None

    def _get_view_method(self, request):
        """Get view method."""
        if hasattr(self, "action"):
            return self.action or None
        return request.method.lower()

    def _get_user(self, request):
        """Get user."""
        user = request.user
        if user.is_anonymous:
            return None
        return user

    def _get_agent(self, request):
        """Get os string"""
        return str(parse(request.META['HTTP_USER_AGENT']))

    def _get_response_ms(self):
        """
        Get the duration of the request response cycle is milliseconds.
        In case of negative duration 0 is returned.
        """
        response_timedelta = now() - self.log["requested_at"]
        response_ms = int(response_timedelta.total_seconds() * 1000)
        return max(response_ms, 0)

    def should_log(self, request, response):
        """
        Method that should return a value that evaluated to True if the request should be logged.
        By default, check if the request method is in logging_methods.
        """
        return self.logging_methods == "__all__" or response.status_code > 404 or response.status_code == 400 \
            or (request.method in self.logging_methods and response.status_code not in [401, 403, 404])

    def _clean_data(self, data):
        """
        Clean a dictionary of data of potentially sensitive info before
        sending to the database.
        Function based on the "_clean_credentials" function of django
        (https://github.com/django/django/blob/stable/1.11.x/django/contrib/auth/__init__.py#L50)

        Fields defined by django are by default cleaned with this function

        You can define your own sensitive fields in your view by defining a set
        eg: sensitive_fields = {'field1', 'field2'}
        """
        if isinstance(data, bytes):
            data = data.decode(errors="replace")

        if isinstance(data, list):
            return [self._clean_data(d) for d in data]

        if isinstance(data, dict):
            SENSITIVE_FIELDS = {
                "api",
                "token",
                "key",
                "secret",
                "password",
                "signature",
            }

            data = dict(data)
            if self.sensitive_fields:
                SENSITIVE_FIELDS = SENSITIVE_FIELDS | {
                    field.lower() for field in self.sensitive_fields
                }

            for key, value in data.items():
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass
                if isinstance(value, (list, dict)):
                    data[key] = self._clean_data(value)
                if key.lower() in SENSITIVE_FIELDS:
                    data[key] = self.CLEANED_SUBSTITUTE
        return data
