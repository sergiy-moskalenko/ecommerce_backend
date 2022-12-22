from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from store.models import Category, Product, Option, Value


class FavoriteMixin:
    def get_favorite(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorites.all().exists()


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
        fields = ('name', 'description', 'price', 'image', 'category',)


class ProductListSerializer(FavoriteMixin, serializers.ModelSerializer):
    favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('image', 'name', 'price', 'favorite')


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

    class Meta:
        model = Product
        fields = ('name', 'image', 'price', 'description', 'options', 'favorite')

    def get_options(self, obj):
        qs_options = Option.objects.filter(products_options__product=obj).distinct().prefetch_related(
            Prefetch(
                'values',
                queryset=Value.objects.filter(products_values__product=obj),
                to_attr='product_values'
            )
        )
        return ProductOptionSerializer(qs_options, many=True).data
