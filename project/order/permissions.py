from rest_framework import permissions


class IsOrderPending(permissions.BasePermission):
    message = 'Updating or deleting closed order is not allowed.'

    def has_object_permission(self, request, view, obj):
        return obj.status == 'P'


class IsOrderByCustomerOrAdmin(permissions.BasePermission):
    """
    Allows access to admin users or to the appropriate customer.
    """

    def has_permission(self, request, view):
        if view.action in ('create',):
            return True
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user or request.user.is_staff




