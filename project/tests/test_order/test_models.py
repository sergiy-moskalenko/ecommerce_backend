from order.models import Order, OrderItem, PaymentData, PaymentStatus


def test_order_creation(db, order_factory):
    order = order_factory()
    assert order is not None
    assert isinstance(order, Order)
    assert str(order) == f'Order #{order.id}'


def test_order_item_creation(db, order_item_factory, product):
    order_item = order_item_factory(product=product)
    assert order_item is not None
    assert isinstance(order_item, OrderItem)
    assert str(order_item) == f'#{order_item.id}'


def test_payment_data_creation(db, payment_data_factory):
    payment_data = payment_data_factory()
    assert payment_data is not None
    assert isinstance(payment_data, PaymentData)
    assert str(payment_data) == f'Callback order #{payment_data.order.id}'


def test_order_save_method(db, order_factory, user_active):
    order = order_factory(customer=user_active)
    assert order.first_name == user_active.first_name
    assert order.last_name == user_active.last_name
    assert order.phone_number == user_active.phone_number


def test_order_save_payment_status(db, order):
    assert not order.paid
    order.payment_status = PaymentStatus.SUCCESS
    order.save()
    assert order.paid


def test_set_payment_status_method(db, order):
    order.set_payment_status(PaymentStatus.SUCCESS)
    assert order.payment_status == PaymentStatus.SUCCESS
    assert order.paid is True  # Assuming PaymentStatus.SUCCESS sets paid to True.
