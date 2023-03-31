from django.db.models import Prefetch
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from order.tgbot import send_message_to_tg
from order.models import OrderItem, Order
from order.permissions import IsOrderByCustomerOrAdmin
from order.serializers import OrderWriteSerializer


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    pass


class OrderView(CreateListRetrieveViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('product')))
    permission_classes = [IsOrderByCustomerOrAdmin]
    serializer_class = OrderWriteSerializer

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return res.filter(customer=user)
        return res

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        headers = self.get_success_headers(serializer.data)
        items_data = data.pop('items')

        order_instance = Order.objects.create(**data)
        objs = [OrderItem(order=order_instance,
                          product=item['product'],
                          price=item['product'].price,
                          discount_price=item['product'].discount_price,
                          quantity=item['quantity']) for item in items_data]
        OrderItem.objects.bulk_create(objs)

        msg_to_tg = f'Order #{order_instance.id} number phone client {order_instance.phone_number}'
        send_message_to_tg(msg_to_tg)

        return Response({'order_number': order_instance.id},
                        status=status.HTTP_201_CREATED,
                        headers=headers)
