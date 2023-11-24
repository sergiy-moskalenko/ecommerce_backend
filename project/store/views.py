from django.db.models import Prefetch, Max, Min
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from store import filters as product_filters
from store import models, schemas, serializers


def get_filtered_categories(category_slug):
    qs_category = models.Category.objects.filter(slug=category_slug)
    return qs_category.get_descendants(include_self=True)


def get_filtered_options(qs_category, qs_categories):
    return models.Option.objects.filter(
        product_filter__category__in=qs_category,
        product_filter__hide=False
    ).order_by('product_filter__position').prefetch_related(
        Prefetch(
            'values',
            queryset=models.Value.objects.filter(
                products_values__product__category__in=qs_categories
            ).distinct(),
            to_attr='product_values'
        )
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get a tree of category lists",
        examples=schemas.CATEGORY_EXAMPLES,
    ),
)
class CategoriesListView(generics.ListAPIView):
    serializer_class = serializers.CategoriesSerializer

    def get_queryset(self):
        return models.Category.objects.get_cached_trees()


@extend_schema(
    summary="Creating product",
    responses=schemas.PRODUCT_POST_RESPONSES,
)
class ProductCreateView(generics.CreateAPIView):
    permission_classes = (permissions.DjangoObjectPermissions | permissions.IsAdminUser,)
    serializer_class = serializers.ProductCreateSerializer
    queryset = models.Product.objects.all()


@extend_schema_view(
    get=extend_schema(
        summary="Get a list of products by category",
        parameters=schemas.PRODUCT_LIST_QUERY_PARAM_EXAMPLES,
    ),
)
class ProductListView(generics.ListAPIView):
    serializer_class = serializers.ProductListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = product_filters.ProductFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # drf-yasg comp
            return models.Product.objects.none()
        qs_categories = get_filtered_categories(self.kwargs['slug'])
        qs = models.Product.objects.filter(category__in=qs_categories)
        user = self.request.user
        # qs = product_filters.product_filter(qs, self.request.query_params)
        if user.is_authenticated:
            return qs.prefetch_related(
                Prefetch('favorites', queryset=models.Favorite.objects.filter(user=self.request.user))
            )
        return qs


@extend_schema(
    summary="Get product by ID",
    responses=schemas.PRODUCT_DETAIL_RESPONSES,
)
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.ProductDetailSerializer
    queryset = models.Product.objects.all()
    lookup_field = 'slug'


@extend_schema_view(
    post=extend_schema(
        summary="Adding favorite product",
        request=None,
        responses=schemas.FAVORITE_POST_RESPONSES,
    ),
    delete=extend_schema(
        summary="Remove favorite product",
        request=None,
        responses=schemas.FAVORITE_DELETE_RESPONSES,
    )
)
class FavoriteProductAddDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    bad_request_message = 'An error has occurred'

    def post(self, request, *args, **kwargs):
        product_slug = self.kwargs['slug']
        product = generics.get_object_or_404(models.Product, slug=product_slug)
        is_exists = product.favorites.filter(user=request.user).exists()
        if not is_exists:
            models.Favorite.objects.create(product=product, user=request.user)
            return Response({'detail': 'User added product'}, status=status.HTTP_200_OK)
        return Response({'detail': self.bad_request_message}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product_slug = self.kwargs['slug']
        models.Favorite.objects.filter(product__slug=product_slug, user=request.user).delete()
        return Response({'detail': 'User deleted product'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Add images to product",
    responses=schemas.PRODUCT_CREATE_IMAGES_RESPONSES
)
class AddProductImagesView(generics.CreateAPIView):
    permission_classes = (permissions.DjangoObjectPermissions | permissions.IsAdminUser,)
    serializer_class = serializers.AddProductImagesSerializer
    queryset = models.Product.objects.all()

    def perform_create(self, serializer):
        product = generics.get_object_or_404(models.Product, slug=self.kwargs.get('slug'))
        serializer.save(product=product)


@extend_schema_view(
    get=extend_schema(
        summary="Get filter of products by category",
        responses=schemas.PRODUCT_FILTER_RESPONSES
    ),
)
class ProductFilterListView(generics.ListAPIView):
    serializer_class = serializers.ProductFilterSerializer

    def get_queryset(self):
        qs_category = models.Category.objects.filter(slug=self.kwargs['slug'])
        qs_categories = qs_category.get_descendants(include_self=True)
        qs = get_filtered_options(qs_category, qs_categories)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        product_price = Coalesce('discount_price', 'price')
        qs_categories = get_filtered_categories(self.kwargs['slug'])
        response_data = models.Product.objects.filter(category__in=qs_categories).aggregate(
            price_min=Min(product_price),
            price_max=Max(product_price)
        )
        response_data['options'] = response.data
        response.data = response_data
        return response
