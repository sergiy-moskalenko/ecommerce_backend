from django.core.validators import MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from phonenumber_field.modelfields import PhoneNumberField


class Order(models.Model):
    PENDING = 'P'
    RETURN = 'R'
    COMPLETED = 'C'

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (RETURN, 'return'),
        (COMPLETED, 'completed')
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = PhoneNumberField(blank=True)
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='orders', null=True,
                                 blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at', 'status')

    def __str__(self):
        return f'Order #{self.id}'

    @cached_property
    def total_cost(self):
        return sum(item.cost for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.customer:
            self.first_name = self.customer.first_name
            self.last_name = self.customer.last_name
            self.phone_number = self.customer.phone_number
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(validators=[MinValueValidator(0)], max_digits=7, decimal_places=2, blank=True)
    discount_price = models.DecimalField(validators=[MinValueValidator(1)], max_digits=7, decimal_places=2,
                                         blank=True, null=True, )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'#{self.id}'

    @cached_property
    def cost(self):
        if not self.discount_price:
            return self.price * self.quantity
        return self.discount_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        if not self.discount_price:
            self.discount_price = self.product.discount_price
        super(OrderItem, self).save(*args, **kwargs)
