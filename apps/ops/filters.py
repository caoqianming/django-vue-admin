from django_filters import rest_framework as filters

from apps.ops.models import DrfRequestLog, Tlog


class DrfLogFilterSet(filters.FilterSet):
    start_request = filters.DateTimeFilter(field_name="requested_at", lookup_expr='gte')
    end_request = filters.DateTimeFilter(field_name="requested_at", lookup_expr='lte')

    class Meta:
        model = DrfRequestLog
        fields = ['id', 'start_request', 'end_request', 'status_code']


class TlogFilterSet(filters.FilterSet):
    start_request = filters.DateTimeFilter(field_name="requested_at", lookup_expr='gte')
    end_request = filters.DateTimeFilter(field_name="requested_at", lookup_expr='lte')

    class Meta:
        model = Tlog
        fields = ['id', 'start_request', 'end_request', 'result']