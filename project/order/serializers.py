from rest_framework import serializers
from order import models
from order.validation import CardValidator


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'product', 'price', 'discount_price', 'quantity', 'cost')
        read_only_fields = ('order', 'price', 'discount_price', 'cost')


class OrderListCreateSerializer(serializers.ModelSerializer):
    customer_id = serializers.HiddenField(default=serializers.CurrentUserDefault(), source='customer', write_only=True)
    # products
    items = OrderItemSerializer(many=True, write_only=True)
    # card fields
    card = serializers.CharField(min_length=16, max_length=16, validators=[CardValidator()],
                                 required=False, write_only=True)
    card_exp_month = serializers.DateField(format='%m', input_formats=['%m'], required=False, write_only=True)
    card_exp_year = serializers.DateField(format='%y', input_formats=['%y'], required=False, write_only=True)
    card_cvv = serializers.CharField(max_length=3, min_length=3, style={'input_type': 'password'},
                                     required=False, write_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'customer_id', 'first_name', 'last_name', 'phone_number',
                  'city', 'address', 'items', 'total_cost', 'payment_mode', 'paid',
                  'card', 'card_exp_month', 'card_exp_year', 'card_cvv',)
        read_only_fields = ('total_cost', 'paid',)
        extra_kwargs = {
            'payment_mode': {'required': True, 'write_only': True},
            'first_name': {'write_only': True},
            'last_name': {'write_only': True},
            'phone_number': {'write_only': True},
        }

    def update_customer_data(self, customer, first_name, last_name):
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate_card_cvv(self, value):
        if not value.isdecimal():
            raise serializers.ValidationError('This CVV is incorrect')
        return value

    def validate(self, attrs):
        customer = attrs.get('customer')
        payment_mode = attrs.get('payment_mode')

        error_msg = 'This field may not be blank.'

        # Validation for non-authenticated users
        if not customer.is_authenticated:
            user_fields = ('first_name', 'last_name', 'phone_number')  # required_fields
            user_errors = {field: error_msg for field in user_fields if not attrs.get(field)}  # missing_fields
            if user_errors:
                raise serializers.ValidationError(user_errors)
            attrs['customer'] = None
        else:  # Authenticated users
            if not customer.first_name or not customer.last_name:
                user_fields = ('first_name', 'last_name')
                user_errors = {field: error_msg for field in user_fields if not attrs.get(field)}
                if user_errors:
                    raise serializers.ValidationError(user_errors)

                self.update_customer_data(customer, attrs['first_name'], attrs['last_name'])

        if payment_mode == models.PaymentMode.CARD:
            card_fields = ('card', 'card_exp_month', 'card_exp_year', 'card_cvv')
            card_errors = {field: error_msg for field in card_fields if not attrs.get(field)}
            if card_errors:
                raise serializers.ValidationError(card_errors)

            attrs['card_exp_month'] = attrs.get('card_exp_month').strftime('%m')
            attrs['card_exp_year'] = attrs.get('card_exp_year').strftime('%y')
        return attrs


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ('id', 'first_name', 'last_name', 'phone_number',
                  'address', 'city', 'items', 'total_cost',
                  'order_status', 'payment_status')
