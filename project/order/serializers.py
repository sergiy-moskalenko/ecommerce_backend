from rest_framework import serializers

from order.models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'price', 'discount_price', 'quantity', 'cost')
        read_only_fields = ('order', 'price', 'discount_price')


class OrderWriteSerializer(serializers.ModelSerializer):
    customer_id = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('customer_id', 'first_name', 'last_name', 'phone_number',
                  'address', 'city', 'items', 'status', 'paid', 'total_cost')
        read_only_fields = ('status', 'paid', 'total_cost')

    def validate(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        phone_number = attrs.get('phone_number')
        items = attrs.get('items')
        request = self.context.get('request')

        if not request.user.is_authenticated:
            if not first_name:
                raise serializers.ValidationError({'first_name': 'This field may not be blank.'})
            if not last_name:
                raise serializers.ValidationError({'last_name': 'This field may not be blank.'})
            if not phone_number:
                raise serializers.ValidationError({'phone_number': 'This field may not be blank.'})
            attrs['customer_id'] = None

        if not items:
            raise serializers.ValidationError({'items': 'This field may not be blank.'})

        return attrs
