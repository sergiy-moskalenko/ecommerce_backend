from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from store.models import Product, Category, Option, Value, ProductOptionValue, Favorite, ProductImage


class ProductImageAdminInline(admin.StackedInline):
    model = ProductImage
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'price', 'is_published',)
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


admin.site.register(ProductOptionValue, ProductOptionValueAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user')


admin.site.register(Favorite, FavoriteAdmin)
