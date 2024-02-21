from django_filters import rest_framework as filters


class MyJsonListFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value in ['all', '']:
            return qs
        elif ',' in value:
            value_l = value.split(',')
            qsx = qs.none()
            for i in value_l:
                qsx = qsx | qs.filter(tags__contains=i)
            return qsx
        else:
            return qs.filter(tags__contains=value)
