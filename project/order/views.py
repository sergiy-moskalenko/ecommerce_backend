from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.response import Response

from order.models import OrderItem, Order
from order.permissions import IsOrderByCustomerOrAdmin, IsOrderPending
from order.serializers import OrderSerializer, OrderWriteSerializer


class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('product')))
    permission_classes = [IsOrderByCustomerOrAdmin]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return OrderWriteSerializer
        return OrderSerializer

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return res.filter(customer=user)
        return res

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            self.permission_classes += [IsOrderPending]
        return super().get_permissions()

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

        return Response({'order_number': order_instance.id},
                        status=status.HTTP_201_CREATED,
                        headers=headers)
