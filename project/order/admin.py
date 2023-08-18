import json
import logging

from django.conf import settings
from django.contrib import admin
from django.db.models.fields.json import JSONField
from django.forms import widgets

from order import models

logger = logging.getLogger(__name__)


class PrettyJSONWidget(widgets.Textarea):
    DEFAULT_ATTR = 'parsed'  # 'raw' or 'parsed'

    def render(self, name, value, attrs=None, **kwargs):
        html = super(PrettyJSONWidget, self).render(name, value, attrs)

        start_as = self.attrs.get("initial", self.DEFAULT_ATTR)

        if start_as not in self._allowed_attrs():
            start_as = self.DEFAULT_ATTR

        return ('<div class="jsonwidget" data-initial="' + start_as +
                '">' '<p><button class="parseraw" '
                'type="button">Show parsed</button> <button class="parsed" '
                'type="button">Collapse all</button> <button class="parsed" '
                'type="button">Expand all</button></p>' + html + '<div class="parsed"></div></div>')

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=4, sort_keys=True)
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(len(row_lengths) + 2, 36)
            self.attrs['cols'] = min(max(row_lengths) + 2, 50)
            return value
        except Exception as e:
            logger.warning("Error while formatting JSON: {}".format(e))
            return super(PrettyJSONWidget, self).format_value(value)

    @staticmethod
    def _allowed_attrs():
        return PrettyJSONWidget.DEFAULT_ATTR, 'parsed'

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        return widgets.Media(
            js=(
                'admin/js/vendor/jquery/jquery%s.js' % extra,
                'admin/js/jquery.init.js',
                'prettyjson/prettyjson.js',
            ),
            css={
                'all': ('prettyjson/prettyjson.css',)
            },
        )


class PaymentDataInline(admin.StackedInline):
    model = models.PaymentData
    fields = ('order', 'data')
    readonly_fields = ('order',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    readonly_fields = ('price', 'discount_price')
    fieldsets = (
        (None, {
            'fields': (
                'product',
                'price',
                'discount_price',
                'quantity',
                'cost',
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'order_status', 'payment_mode', 'payment_status', 'paid', 'total_cost',
                    'created_at', 'updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'registered')
    inlines = (OrderItemInline, PaymentDataInline)

    def registered(self, obj):
        return bool(obj.customer)

    registered.boolean = True

    fieldsets = (
        ('PERSONAL INFO', {
            'fields': (
                ('first_name', 'last_name', 'registered',),
                'phone_number',
                ('city', 'address'),

            )
        }),
        ('STATUSES', {
            'fields': (
                'order_status',
                'payment_mode',
                'payment_status',
                ('total_cost', 'paid'),
            )
        }),
        ('DATE', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    radio_fields = {
        'order_status': admin.HORIZONTAL,
        'payment_status': admin.HORIZONTAL,
        'payment_mode': admin.HORIZONTAL,
    }

    @admin.display(description='customer')  # ordering=Concat("first_name", Value(" "), "last_name"),
    def full_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        super().save_model(request, obj, form, change)
