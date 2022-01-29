from django_filters import rest_framework as filters
from .models import Ticket
class TicketFilterSet(filters.FilterSet):
    start_create = filters.DateFilter(field_name="create_time", lookup_expr='gte')
    end_create = filters.DateFilter(field_name="create_time", lookup_expr='lte')
    category = filters.ChoiceFilter(choices = Ticket.category_choices, method='filter_category')

    class Meta:
        model = Ticket
        fields = ['workflow', 'state', 'act_state', 'start_create', 'end_create', 'category']

    def filter_category(self, queryset, name, value):
        user=self.request.user
        if value == 'owner': # 我的
            queryset = queryset.filter(create_by=user)
        elif value == 'duty': # 待办
            queryset = queryset.filter(participant__contains=user.id).exclude(act_state__in=[Ticket.TICKET_ACT_STATE_FINISH, Ticket.TICKET_ACT_STATE_CLOSED])
        elif value == 'worked': # 处理过的
            queryset = queryset.filter(ticketflow_ticket__participant=user).exclude(create_by=user).order_by('-update_time').distinct()
        elif value == 'cc': # 抄送我的
            queryset = queryset.filter(ticketflow_ticket__participant_cc__contains=user.id).exclude(create_by=user).order_by('-update_time').distinct()
        elif value == 'all':
            pass
        else:
            queryset = queryset.none()
        return queryset