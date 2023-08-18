import logging

from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from order import models
from order import payment
from order.permissions import IsOrderByCustomer
from order import serializers
from order.tgbot import send_message_to_tg

logger = logging.getLogger(__name__)


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOrderByCustomer]
    serializer_class = serializers.OrderListCreateSerializer

    def get_queryset(self):
        user = self.request.user
        return models.Order.objects.select_related('customer').prefetch_related(
            Prefetch(
                'items',
                queryset=models.OrderItem.objects.select_related('product'))
        ).filter(customer=user)

    @staticmethod
    def get_cost(item):
        return (item['product'].discount_price or item['product'].price) * item['quantity']

    def get_total_cost(self, items_data):
        return sum(self.get_cost(item)
                   for item in items_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        headers = self.get_success_headers(serializer.data)

        items_data = data.pop('items')
        payment_mode = data.get('payment_mode')
        card_data = {k: data.pop(k) for (k, v) in data.copy().items() if 'card' in k}
        total_cost = self.get_total_cost(items_data)
        order_instance = models.Order.objects.create(**data, total_cost=total_cost)
        objs = [models.OrderItem(order=order_instance,
                                 product=item['product'],
                                 price=item['product'].price,
                                 discount_price=item['product'].discount_price,
                                 quantity=item['quantity'],
                                 cost=self.get_cost(item)
                                 )
                for item in items_data]
        models.OrderItem.objects.bulk_create(objs)

        msg_to_tg = f'Order #{order_instance.id} number phone client {order_instance.phone_number}'
        send_message_to_tg(msg_to_tg)

        if payment_mode == models.PaymentMode.CARD:
            result_pay = payment.LiqPayCard(
                order_id=str(order_instance.id),
                amount=str(order_instance.total_cost),
                phone=str(order_instance.phone_number),
                **card_data
            )
            result_pay.api()

        return Response({'order_number': order_instance.id},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsOrderByCustomer]
    serializer_class = serializers.OrderDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return models.Order.objects.select_related('customer').prefetch_related(
            Prefetch(
                'items',
                queryset=models.OrderItem.objects.select_related('product')
            )
        ).filter(customer=user)


class PayCallbackView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        signature = request.data.get('signature')

        if not signature:
            logger.error(f"server request hasn't parameter signature, request_data:\n{request.data}")
        if not data:
            logger.error(f"server request hasn't parameter data, request_data:\n{request.data}")

        res_data = payment.Callback.callback(data, signature)
        order_id = res_data['order_id']
        payment_status = res_data['status']
        try:
            obj = models.Order.objects.get(id=order_id)
            obj.set_payment_status(payment_status)
            models.PaymentData.objects.create(order_id=order_id, data=res_data)
        except models.Order.DoesNotExist:
            logger.error(f"Order not found:\n{res_data}")
        return Response({"result": "ok"})
