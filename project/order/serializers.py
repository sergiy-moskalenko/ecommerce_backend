from rest_framework import serializers
from rest_framework.serializers import ListField
from django.conf import settings
from order import models
from order.validation import CardValidator


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'product', 'price', 'discount_price', 'quantity', 'cost')
        read_only_fields = ('order', 'price', 'discount_price')


class OrderListCreateSerializer(serializers.ModelSerializer):
    customer_id = serializers.HiddenField(default=serializers.CurrentUserDefault(), source='customer', write_only=True)
    # products
    items = OrderItemSerializer(many=True, write_only=True)  # == items = ListField(child=OrderItemSerializer())
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
                  'city', 'address', 'items', 'total_cost', 'payment_mode', 'paid', 'total_cost',
                  'card', 'card_exp_month', 'card_exp_year', 'card_cvv',)
        read_only_fields = ('total_cost', 'paid',)
        extra_kwargs = {
            'payment_mode': {'required': True},
            'first_name': {'write_only': True},
            'last_name': {'write_only': True},
            'phone_number': {'write_only': True},
        }

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate_card_cvv(self, value):
        if not value.isdecimal():
            raise serializers.ValidationError('This CVV is incorrect')
        return value

    def validate(self, attrs):
        errors_dict = dict()
        error_msg = 'This field may not be blank.'
        request = self.context.get('request')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        phone_number = attrs.get('phone_number')

        payment_mode = attrs.get('payment_mode')
        card = attrs.get('card')
        card_exp_month = attrs.get('card_exp_month')
        card_exp_year = attrs.get('card_exp_year')
        card_cvv = attrs.get('card_cvv')

        if not request.user.is_authenticated:
            if not first_name:
                errors_dict.update({'first_name': error_msg})
            if not last_name:
                errors_dict.update({'last_name': error_msg})
            if not phone_number:
                errors_dict.update({'phone_number': error_msg})
            attrs['customer_id'] = None
            if errors_dict:
                raise serializers.ValidationError(errors_dict)

        if payment_mode == models.PaymentMode.CARD:
            if not card:
                errors_dict.update({'card': error_msg})
            if not card_exp_month:
                errors_dict.update({'card_exp_month': error_msg})
            if not card_exp_year:
                errors_dict.update({'card_exp_year': error_msg})
            if not card_cvv:
                errors_dict.update({'card_cvv': error_msg})

            if errors_dict:
                raise serializers.ValidationError(errors_dict)

            attrs['card_exp_month'] = card_exp_month.strftime('%m')
            attrs['card_exp_year'] = card_exp_year.strftime('%y')
        return attrs


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ('id', 'first_name', 'last_name', 'phone_number',
                  'address', 'city', 'items', 'paid', 'total_cost',)
