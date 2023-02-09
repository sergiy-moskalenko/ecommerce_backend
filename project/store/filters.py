from django_filters import rest_framework as filters
from store.models import Value


class ProductFilter(filters.FilterSet):
    price = filters.RangeFilter()
    value = filters.CharFilter(field_name='value', method='filter_value')
    q = filters.CharFilter(field_name='name', lookup_expr='icontains')
    o = filters.OrderingFilter(
        fields=(
            ('price', 'price'),
        ),
    )

    def filter_value(self, queryset, name, value):
        if value:
            value = value.split(',')
            qs_option = Value.objects.filter(id__in=value).values_list('option__id', 'id')
            dict_query = {}
            for k, v in qs_option:
                if k in dict_query.keys():
                    dict_query[k] += [v]
                else:
                    dict_query[k] = [v]
            for _, value in dict_query.items():
                queryset = queryset.filter(options_values__value__in=value)
        return queryset


def product_filter(queryset, query_params):
    """A filter with query parameters, e.g: ?10=29,30&11=32"""
    qs = queryset
    query = dict(query_params)
    search_query = ''.join(query.pop('s', ''))
    price_min_query = ''.join(query.pop('price_min', ''))
    price_max_query = ''.join(query.pop('price_max', ''))
    order_price = ''.join(query.pop('o', ''))

    for option, value in query.items():
        s = ''.join(i if i.isdigit() else ' ' for i in ','.join(value))
        value = [i for i in s.split()]
        qs = qs.filter(options_values__option=option,
                       options_values__value__in=value)
    if price_max_query:
        qs = qs.filter(price__lte=price_max_query)
    if price_min_query:
        qs = qs.filter(price__gte=price_min_query)
    if order_price:
        qs = qs.order_by(order_price)
    if search_query:
        qs = qs.filter(name__icontains=search_query)
    return qs
