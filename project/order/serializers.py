from rest_framework import serializers

from order.models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'price', 'discount_price', 'quantity', 'cost')
        read_only_fields = ('order', 'price', 'discount_price')


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.get_full_name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'first_name', 'last_name', 'phone_number',
                  'address', 'city', 'items', 'status', 'total_cost')


class OrderWriteSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('customer', 'first_name', 'last_name', 'phone_number',
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
            attrs['customer'] = None

        if not items:
            raise serializers.ValidationError({'items': 'This field may not be blank.'})

        return attrs

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)

        # variant #1
        # items_id_pool = []
        # for item in items_data:
        #     product = item['product']
        #     try:
        #         order_item = instance.items.get(product=product)
        #         order_item.product = item.get('product', order_item.product)
        #         order_item.quantity = item.get('quantity', order_item.quantity)
        #         order_item.save()
        #         items_id_pool.append(order_item.id)
        #     except OrderItem.DoesNotExist:
        #         del item['id']
        #         order_item = OrderItem.objects.create(order=instance, **item)
        #         items_id_pool.append(order_item.id)
        #
        # instance.items.exclude(id__in=items_id_pool).delete()

        # variant #2
        # items_id_pool = []
        # items_id_list = [item['id'] for item in items_data if 'id' in item.keys()]
        # items_in_bulk = instance.items.in_bulk(items_id_list)
        # for item in items_data:
        #     item_id = item.get('id')
        #     if item_id in items_in_bulk.keys():
        #         order_item = items_in_bulk[item_id]
        #         order_item.product = item.get('product', order_item.product)
        #         order_item.quantity = item.get('quantity', order_item.quantity)
        #         order_item.save()
        #         items_id_pool.append(item_id)
        #     else:
        #         if 'id' in item.keys():
        #             del item['id']
        #         order_item = OrderItem.objects.create(order=instance, **item)
        #         items_id_pool.append(order_item.id)
        #
        # instance.items.exclude(id__in=items_id_pool).delete()
        # return instance

        # variant #3
        objs_items_create = []
        objs_items_update = []
        items_id_list = [item['id'] for item in items_data if 'id' in item.keys()]
        items_in_bulk = instance.items.in_bulk(items_id_list)
        for item in items_data:
            item_id = item.get('id')
            if item_id in items_in_bulk.keys():
                order_item = items_in_bulk[item_id]
                objs_items_update.append(items_in_bulk[item_id])
                order_item.product = item.get('product', order_item.product)
                order_item.quantity = item.get('quantity', order_item.quantity)
                order_item.price = order_item.product.price
                order_item.discount_price = order_item.product.price
            else:
                if 'id' in item.keys():
                    del item['id']
                objs_items_create.append(OrderItem(order=instance,
                                                   product=item['product'],
                                                   price=item['product'].price,
                                                   discount_price=item['product'].discount_price,
                                                   quantity=item['quantity']))

        objs_items = OrderItem.objects.bulk_create(objs_items_create)

        update_fields = ['product', 'quantity', 'price', 'discount_price']
        OrderItem.objects.bulk_update(objs_items_update, update_fields)

        objs_items.extend(objs_items_update)
        items_id_pool = [obj.id for obj in objs_items]
        instance.items.exclude(id__in=items_id_pool).delete()

        return instance
