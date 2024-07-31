from django_filters import rest_framework as filters
from .models import Dept, User


class UserFilterSet(filters.FilterSet):

    class Meta:
        model = User
        fields = {
            'name': ['exact', 'contains'],
            'is_deleted': ['exact'],
            'posts': ['exact'],
            'post': ['exact'],
            'belong_dept': ['exact'],
            'depts': ['exact'],
            'type': ['exact', 'in'],
            'belong_dept__name': ['exact'],
            'depts__name': ["exact", "contains"],
            'posts__name': ["exact", "contains"],
            'posts__code': ["exact", "contains"], 
        }


class DeptFilterSet(filters.FilterSet):

    class Meta:
        model = Dept
        fields = {
            'type': ['exact', 'in'],
            'name': ['exact', 'in', 'contains']
        }
