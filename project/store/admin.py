from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from store.models import (
    Category,
    Favorite,
    Product,
    ProductFilter,
    ProductImage,
    ProductOptionValue,
    Option,
    Value,
)


class ProductImageAdminInline(admin.StackedInline):
    model = ProductImage
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'price', 'discount_price', 'discount_percent', 'is_published',)
    inlines = (
        ProductImageAdminInline,
    )


admin.site.register(Product, ProductAdmin)


class CategoryAdmin(DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('tree_actions', 'indented_title', 'slug', 'hide')
    list_display_links = ('indented_title',)
    expand_tree_by_default = True
    mptt_level_indent = 30
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )


admin.site.register(Category, CategoryAdmin)


class ValueAdmin(admin.TabularInline):
    model = Value


class OptionAdmin(admin.ModelAdmin):
    inlines = [
        ValueAdmin,
    ]


admin.site.register(Option, OptionAdmin)


class ProductOptionValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'value')
    ordering = ('product', 'option')


admin.site.register(ProductOptionValue, ProductOptionValueAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user')


admin.site.register(Favorite, FavoriteAdmin)


class ProductFilterAdmin(admin.ModelAdmin):
    list_display = ('category', 'option', 'position', 'hide')
    ordering = ('-category', 'position')
    list_filter = ('category', )


admin.site.register(ProductFilter, ProductFilterAdmin)
