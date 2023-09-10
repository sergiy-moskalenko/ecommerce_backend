from django.db.models import Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from store import models


class FavoriteMixin:
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_favorite(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorites.exists()


class CategoriesSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.Category
        fields = ('name', 'slug', 'children',)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_children(self, obj):
        children = obj.get_children()
        return CategoriesSerializer(children, many=True).data


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('name', 'description', 'price', 'discount_price', 'image', 'category')


class ProductListSerializer(FavoriteMixin, serializers.ModelSerializer):
    favorite = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ('id', 'image', 'name', 'slug', 'price', 'discount_price', 'favorite')


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Value
        fields = ('id', 'name',)


class ProductOptionSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        model = models.Option
        fields = ('id', 'name', 'values')

    @extend_schema_field(ValueSerializer(many=True))
    def get_values(self, obj):
        qs_values = obj.product_values
        return ValueSerializer(qs_values, many=True).data


class ProductDetailSerializer(FavoriteMixin, serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ('name', 'image', 'price', 'description', 'options', 'favorite', 'images')

    @extend_schema_field(ProductOptionSerializer(many=True))
    def get_options(self, obj):
        qs_options = models.Option.objects.filter(products_options__product=obj).distinct().prefetch_related(
            Prefetch(
                'values',
                queryset=models.Value.objects.filter(products_values__product=obj),
                to_attr='product_values'
            )
        )
        return ProductOptionSerializer(qs_options, many=True).data

    @extend_schema_field(serializers.ListField())
    def get_images(self, obj):
        request = self.context.get('request')
        urls = []
        for image in obj.images.all():
            urls.append(request.build_absolute_uri(image.image.url))
        return urls


class AddProductImagesSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(use_url=False),
        write_only=True, max_length=5
    )

    class Meta:
        model = models.Product
        fields = ('images',)

    def create(self, validated_data):
        images = validated_data['images']
        product = validated_data['product']
        objs = [models.ProductImage(product=product, image=image) for image in images]
        models.ProductImage.objects.bulk_create(objs)
        return product


class ProductFilterSerializer(ProductOptionSerializer):
    pass
