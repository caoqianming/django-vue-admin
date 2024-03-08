from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError


class MyPagination(PageNumberPagination):
    """
    自定义分页/传入page为0则不分页
    """
    page_size = 10
    page_size_query_param = 'page_size'

    def get_page_number(self, request, paginator):
        if 'page' in request.data:
            request.query_params['page'] = request.data['page']
            del request.data['page']
        return super().get_page_number(request, paginator)

    def get_page_size(self, request):
        if 'page_size' in request.data:
            request.query_params['page_size'] = request.data['page_size']
            del request.data['page_size']
        return super().get_page_size(request)

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('pageoff', None) or request.query_params.get('page', None) == '0':
            if queryset.count() < 800:
                return None
            raise ParseError('单次请求数据量大,请分页获取')
        return super().paginate_queryset(queryset, request, view=view)
