import pytest

from order.permissions import IsOrderByCustomer


@pytest.fixture
def order_permission():
    return IsOrderByCustomer()


@pytest.fixture
def order_user_active(order_factory, user_active):
    return order_factory(customer=user_active)


@pytest.fixture
def order_user_another(order_factory, user_another):
    return order_factory(customer=user_another)


@pytest.mark.django_db
class TestIsOrderByCustomer:
    def test_has_permission_authenticated_user(self, request_user_active, order_permission):
        assert order_permission.has_permission(request_user_active, None)

    def test_has_permission_unauthenticated_user(self, request_anonymous_user, order_permission):
        assert not order_permission.has_permission(request_anonymous_user, None)

    def test_has_object_permission_matching_customer(self, request_user_active, order_user_active, order_permission):
        assert order_permission.has_object_permission(request_user_active, None, order_user_active)

    def test_has_object_permission_non_matching_customer(self, request_user_active, order_user_another,
                                                         order_permission):
        assert not order_permission.has_object_permission(request_user_active, None, order_user_another)

    def test_has_object_permission_post_method(self, request_user_active, order_user_active, order_permission):
        request_user_active.method = 'POST'
        assert order_permission.has_object_permission(request_user_active, None, order_user_active)
