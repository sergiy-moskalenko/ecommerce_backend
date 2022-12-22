from django.db.models import Prefetch
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Category, Product, Favorite
from store.serializers import (CategoriesSerializer,
                               ProductCreateSerializer,
                               ProductListSerializer,
                               ProductDetailSerializer)


class CategoriesListView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    queryset = Category.objects.get_cached_trees()


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    queryset = Product.objects.all()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Category.objects.filter(slug=self.kwargs['slug'])
        qs_category = qs.get_descendants(include_self=True)
        qs_product = Product.objects.filter(category__in=qs_category)
        user = self.request.user
        if user.is_authenticated:
            return qs_product.prefetch_related(
                Prefetch('favorites', queryset=Favorite.objects.filter(user=self.request.user))
            )
        return qs_product


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'


class FavoriteProductAddDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
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
