from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from store.models import Category, Product, Option, Value, ProductImage


class FavoriteMixin:
    def get_favorite(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorites.exists()


class CategoriesSerializer(serializers.ModelSerializer):
    children = SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'slug', 'children',)

    def get_children(self, obj):
        children = obj.get_children()
        return CategoriesSerializer(children, many=True).data


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'discount_price', 'image', 'category')


class ProductListSerializer(FavoriteMixin, serializers.ModelSerializer):
    favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('image', 'name', 'price', 'discount_price', 'favorite')


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ('id', 'name',)


class ProductOptionSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ('id', 'name', 'values')

    def get_values(self, obj):
        qs_values = obj.product_values
        return ValueSerializer(qs_values, many=True).data


class ProductDetailSerializer(FavoriteMixin, serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'image', 'price', 'description', 'options', 'favorite', 'images')

    def get_options(self, obj):
        qs_options = Option.objects.filter(products_options__product=obj).distinct().prefetch_related(
            Prefetch(
                'values',
                queryset=Value.objects.filter(products_values__product=obj),
                to_attr='product_values'
            )
        )
        return ProductOptionSerializer(qs_options, many=True).data

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
        model = Product
        fields = ('images',)

    def create(self, validated_data):
        images = validated_data['images']
        product = validated_data['product']
        objs = [ProductImage(product=product, image=image) for image in images]
        ProductImage.objects.bulk_create(objs)
        return product


class FilterSerializer(ProductOptionSerializer):
    pass
