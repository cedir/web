"""Custom DRF Permission classes"""
from rest_framework.exceptions import ParseError
from rest_framework.permissions import BasePermission

__all__ = ['IsAuthenticatedOrOptions',]


class IsAuthenticatedOrOptions(BasePermission):
    """
        Allows access only to authenticated users.
        Allow OPTIONS requests without being logged
    """
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return request.user and request.user.is_authenticated()

