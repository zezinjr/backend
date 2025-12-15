from django_filters import rest_framework as filters

from core.models import Client

LIKE = 'unaccent__icontains'
EQUALS = 'exact'
IN = 'in'
LT = 'lt'
GT = 'gt'
LTE = 'lte'
GTE = 'gte'


class ClientFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", lookup_expr='exact')
    age = filters.NumberFilter(field_name="age", lookup_expr='gt')

    class Meta:
        model = Client
        fields = ['name', 'age', 'rg']
