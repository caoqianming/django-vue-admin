import json
from user_agents import parse


def get_request_ip(request):
    """
    获取请求IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
        return ip
    ip = request.META.get('REMOTE_ADDR', '') or getattr(request, 'request_ip', None)
    return ip or 'unknown'


def get_request_data(request):
    """
    获取请求参数
    """
    request_data = getattr(request, 'request_data', None)
    if request_data:
        return request_data
    data: dict = {**request.GET.dict(), **request.POST.dict()}
    if not data:
        try:
            body = request.body
            if body:
                data = json.loads(body)
        except Exception:
            pass
        if not isinstance(data, dict):
            data = {'data': data}
    return data


def get_request_path(request, *args, **kwargs):
    """
    获取请求路径
    """
    request_path = getattr(request, 'request_path', None)
    if request_path:
        return request_path
    values = []
    for arg in args:
        if len(arg) == 0:
            continue
        if isinstance(arg, str):
            values.append(arg)
        elif isinstance(arg, (tuple, set, list)):
            values.extend(arg)
        elif isinstance(arg, dict):
            values.extend(arg.values())
    if len(values) == 0:
        return request.path
    path: str = request.path
    for value in values:
        path = path.replace('/' + value, '/' + '{id}')
    return path


def get_browser(request, ):
    """
    获取浏览器名
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)
    return user_agent.get_browser()


def get_os(request, ):
    """
    获取操作系统
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)
    return user_agent.get_os()


def get_verbose_name(queryset=None, view=None, model=None):
    """
    获取 verbose_name
    :param request:
    :param view:
    :return:
    """
    try:
        if queryset and hasattr(queryset, 'model'):
            model = queryset.model
        elif view and hasattr(view.get_queryset(), 'model'):
            model = view.get_queryset().model
        elif view and hasattr(view.get_serializer(), 'Meta') and hasattr(view.get_serializer().Meta, 'model'):
            model = view.get_serializer().Meta.model
        if model:
            return getattr(model, '_meta').verbose_name
        else:
            model = queryset.model._meta.verbose_name
    except Exception:
        pass
    return model if model else ""
