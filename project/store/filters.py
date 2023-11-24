from collections import defaultdict

from django.db.models import Q
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters

from store.models import Value


class CustomOrderFilter(filters.OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('price', 'Price'),
            ('-price', 'Price (descending)'),
        ]

    def filter(self, qs, value):
        if value and any(v in ['price', '-price'] for v in value):
            return order_by_price(qs, value)
        return super().filter(qs, value)


def order_by_price(queryset, value: list):
    order_field = Coalesce('discount_price', 'price')
    if '-price' in value:
        queryset = queryset.order_by(order_field.desc(), '-price')
    if 'price' in value:
        queryset = queryset.order_by(order_field.asc(), 'price')
    return queryset


class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price_min', method='filter_price_min', label='Price min')
    price_max = filters.NumberFilter(field_name='price_max', method='filter_price_max', label='Price max')
    value = filters.CharFilter(field_name='value', method='filter_value', label='Values')
    s = filters.CharFilter(field_name='name', lookup_expr='icontains')
    o = CustomOrderFilter()

    def filter_price_min(self, queryset, name, value):
        return filter_by_price(queryset, price_min=value)

    def filter_price_max(self, queryset, name, value):
        return filter_by_price(queryset, price_max=value)

    def filter_value(self, queryset, name, value):
        queryset = filter_by_values(queryset, value)
        return queryset


def filter_by_price(queryset, price_min=None, price_max=None):
    price_filters = Q()
    if price_max:
        price_filters &= Q(discount_price__lte=price_max) | Q(price__lte=price_max)
    if price_min:
        price_filters &= Q(discount_price__gte=price_min) | Q(price__gte=price_min)
    return queryset.filter(price_filters)


def filter_by_values(queryset, value):
    if value:
        value_ids = value.split(',')
        option_value_ids = Value.objects.filter(id__in=value_ids).values_list('option__id', 'id')
        option_id_to_values = defaultdict(list)
        for option_id, value_id in option_value_ids:
            option_id_to_values[option_id].append(value_id)
        for values_ids in option_id_to_values.values():
            queryset = queryset.filter(options_values__value__in=values_ids)
    return queryset


def product_filter(queryset, query_params):
    """Custom filter"""

    search_query = query_params.get('s', '')
    price_min_query = query_params.get('price_min', '')
    price_max_query = query_params.get('price_max', '')
    order_price = query_params.get('o', '')

    queryset = filter_by_option_and_values(queryset, query_params)
    queryset = filter_by_price(queryset, price_min_query, price_max_query)
    queryset = order_by_price(queryset, [order_price])
    queryset = filter_by_name(queryset, search_query)

    return queryset


def filter_by_option_and_values(queryset, query_params):
    # The filter with query parameters, e.g: ?10=29,30&11=32
    for option, values in query_params.items():
        if option.isdecimal():
            # Extract only numeric characters from the values (example: '12qw, 18   , 20')
            numeric_values = ''.join(v for v in values if v.isdecimal() or v == ',')
            # Split the resulting string by commas (example: ['12', '18', '20'])
            values_ids = numeric_values.split(',')
            queryset = queryset.filter(
                options_values__option=option,
                options_values__value__in=values_ids
            )

    # The filter with query parameters, e.g: ?29,30,32"""
    queryset = filter_by_values(queryset, query_params.get('value', None))
    return queryset


def filter_by_name(queryset, search_query):
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)
    return queryset
