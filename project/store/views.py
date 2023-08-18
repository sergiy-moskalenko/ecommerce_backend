from django.db.models import Prefetch, Max, Min
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    DjangoObjectPermissions,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from store.filters import ProductFilter, product_filter
from store.models import Category, Favorite, Product, Option, Value
from store.serializers import (
    AddProductImagesSerializer,
    CategoriesSerializer,
    FilterSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoriesListView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    queryset = Category.objects.get_cached_trees()


class ProductCreateView(generics.CreateAPIView):
    permission_classes = (DjangoObjectPermissions | IsAdminUser,)
    serializer_class = ProductCreateSerializer
    queryset = Product.objects.all()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs_category = Category.objects.filter(slug=self.kwargs['slug'])
        qs_category_in = qs_category.get_descendants(include_self=True)
        qs = Product.objects.filter(category__in=qs_category_in)
        user = self.request.user
        qs = product_filter(qs, self.request.query_params)
        if user.is_authenticated:
            return qs.prefetch_related(
                Prefetch('favorites', queryset=Favorite.objects.filter(user=self.request.user))
            )
        return qs

    permission_classes = (AllowAny,)
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'


class FavoriteProductAddDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    bad_request_message = 'An error has occurred'

    def post(self, request, *args, **kwargs):
        product_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=product_slug)
        is_exists = Favorite.objects.filter(product=product, user=request.user).exists()
        if not is_exists:
            Favorite.objects.create(product=product, user=request.user)
            return Response({'detail': 'User added product'}, status=status.HTTP_200_OK)
        return Response({'detail': self.bad_request_message}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product_slug = self.kwargs['slug']
        Favorite.objects.filter(product__slug=product_slug, user=request.user).delete()
        return Response({'detail': 'User deleted product'}, status=status.HTTP_200_OK)


class AddProductImagesView(generics.CreateAPIView):
    permission_classes = (DjangoObjectPermissions | IsAdminUser,)
    serializer_class = AddProductImagesSerializer
    queryset = Product.objects.all()

    def perform_create(self, serializer):
        product = get_object_or_404(Product, slug=self.kwargs.get('slug'))
        serializer.save(product=product)


class ProductFilterListView(generics.ListAPIView):
    serializer_class = FilterSerializer

    def get_queryset(self):
        qs_category = Category.objects.filter(slug=self.kwargs['slug'])
        qs_category_in = qs_category.get_descendants(include_self=True)
        qs = Option.objects.filter(
            product_filter__category__in=qs_category,
            product_filter__hide=False
        ) \
            .order_by('product_filter__position') \
            .prefetch_related(
            Prefetch('values',
                     queryset=Value.objects.filter(products_values__product__category__in=qs_category_in).distinct(),
                     to_attr='product_values')
        )
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        product_price = Coalesce('discount_price', 'price')
        qs_category = Category.objects.filter(slug=self.kwargs['slug'])
        qs_category_in = qs_category.get_descendants(include_self=True)
        response_data = Product.objects.filter(category__in=qs_category_in).aggregate(
            price_min=Min(product_price),
            price_max=Max(product_price))
        response_data['filters'] = response.data
        response.data = response_data
        return response
