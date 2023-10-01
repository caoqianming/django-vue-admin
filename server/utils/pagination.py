from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError

class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('pageoff', None) or request.query_params.get('page', None) == '0':
            if queryset.count() < 800:
                return None
            raise ParseError('单次请求数据量大,请分页获取')
        return super().paginate_queryset(queryset, request, view=view)

class PageOrNot:
    def paginate_queryset(self, queryset):
        if (self.paginator is None):
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count()<500:
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count()>=500:
            raise ParseError('单次请求数据量大,请求中止')
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
