import django_filters

from apps.shop.models import Product, Review


class ProductFilter(django_filters.FilterSet):
    max_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='gte')
    in_stock = django_filters.NumberFilter(lookup_expr='gte')
    created_at = django_filters.DateTimeFilter(lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['max_price', 'min_price', 'in_stock', 'created_at']


class ReviewFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='lte')
    date_after = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')

    ordering_rating = django_filters.OrderingFilter(
        fields=(
            ('rating', 'increase'),
            ('-rating', 'decrease'),

        )
    )
    ordering_created = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'increase'),
            ('-created_at', 'decrease'),

        )
    )

    class Meta:
        model = Review
        fields = ['rating', 'created_at']
