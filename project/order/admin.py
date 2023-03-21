from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price', 'discount_price')
    fieldsets = (
        (None, {
            'fields': (
                'product',
                'price',
                'discount_price',
                'quantity',
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'paid',
                    'created_at', 'updated_at', 'total_cost')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (OrderItemInline,)

    fieldsets = (
        (None, {
            'fields': (
                'customer',
                'first_name',
                'last_name',
                'phone_number',
                'status',
                'paid',
                'address',
                'city',
                'created_at',
                'updated_at',

            )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Order, OrderAdmin)
