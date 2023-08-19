from django.contrib import admin
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from store import models


class ProductImageAdminInline(admin.StackedInline):
    model = models.ProductImage
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'price', 'discount_price', 'discount_percent', 'is_published',)
    inlines = (ProductImageAdminInline,)
    fieldsets = (
        (None, {
            'fields': (
                'category',
                ('name', 'slug'),
                ('price', 'discount_price'),
                'description',
                'is_published',
                ('image', 'headshot_image'),
            )
        }),
    )

    readonly_fields = ["headshot_image"]

    def headshot_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="15%" height="15%" />')

    headshot_image.short_description = ''


admin.site.register(models.Product, ProductAdmin)


class CategoryAdmin(DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('tree_actions', 'indented_title', 'slug', 'hide')
    list_display_links = ('indented_title',)
    expand_tree_by_default = True
    mptt_level_indent = 30
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )


admin.site.register(models.Category, CategoryAdmin)


class ValueAdmin(admin.TabularInline):
    model = models.Value


class OptionAdmin(admin.ModelAdmin):
    inlines = [
        ValueAdmin,
    ]


admin.site.register(models.Option, OptionAdmin)


class ProductOptionValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'value')
    ordering = ('product', 'option')


admin.site.register(models.ProductOptionValue, ProductOptionValueAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user')


admin.site.register(models.Favorite, FavoriteAdmin)


class ProductFilterAdmin(admin.ModelAdmin):
    list_display = ('category', 'option', 'position', 'hide')
    ordering = ('-category', 'position')
    list_filter = ('category',)


admin.site.register(models.ProductFilter, ProductFilterAdmin)
