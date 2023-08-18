from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class PaymentStatus(models.TextChoices):
    SUCCESS = 'success', 'Success'
    ERROR = 'error', 'Error'
    REVERSED = 'reversed', 'Reversed'
    FAILURE = 'failure', 'Failure'
    PROCESSING = 'processing', 'Processing'
    __empty__ = 'Unknown'


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    RETURN = 'return', 'Return'
    SHIPMENT = 'shipment', 'Awaiting Shipment'
    PICKUP = 'pickup', 'Awaiting Pickup'
    SHIPPED = 'shipped', 'Shipped'
    CANCELLED = 'cancelled', 'Cancelled'
    COMPLETED = 'completed', 'Completed'


class PaymentMode(models.TextChoices):
    CASH = 'cash', 'Payment upon receipt of goods'
    CARD = 'card', 'Credit and debit card'


class Order(models.Model):
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = PhoneNumberField(blank=True)
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='orders',
                                 null=True, blank=True)

    order_status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_mode = models.CharField(max_length=50, choices=PaymentMode.choices, default=PaymentMode.CARD)
    payment_status = models.CharField(max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.__empty__)

    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    total_cost = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order #{self.id}'

    def save(self, *args, **kwargs):
        if self.payment_status == PaymentStatus.SUCCESS:
            self.paid = True
        if self.customer:
            self.first_name = self.customer.first_name
            self.last_name = self.customer.last_name
            self.phone_number = self.customer.phone_number
        super().save(*args, **kwargs)

    def set_payment_status(self, payment_status):
        self.payment_status = PaymentStatus.__empty__
        if payment_status in PaymentStatus.values:
            self.payment_status = payment_status
        self.save()
        return self


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, )
    quantity = models.PositiveIntegerField(default=1)

    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_price_not_negative",
                check=models.Q(price__gt=0),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_discount_price_not_zero",
                check=models.Q(discount_price__gt=0) | models.Q(discount_price__isnull=True),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_discount_price_less_than_price",
                check=models.Q(price__gt=models.F('discount_price')),
            )
        ]

    def __str__(self):
        return f'#{self.id}'


class PaymentData(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_data')
    data = models.JSONField()

    class Meta:
        verbose_name = 'Payment data'
        verbose_name_plural = 'Payment data'

    def __str__(self):
        return f'Callback order #{self.order.id}'
