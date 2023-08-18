from rest_framework import permissions


class IsOrderByCustomer(permissions.BasePermission):
    """
    Allows the corresponding client to access.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user
