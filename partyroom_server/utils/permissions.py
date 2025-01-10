from logging import getLogger

from django.conf import settings
from rest_framework import permissions
from utils.utils import check_write_review_permissions

logger = getLogger('permissions')

class IsBookedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return check_write_review_permissions(request)


class IsVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # permission check when create
        return request.user.is_verified


class IsNonVerifiedUser(permissions.BasePermission):
    """Only non-verified user can delete via api
    """
    def has_permission(self, request, view):
        return not request.user.is_verified


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsBookingOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff


class IsRoomerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        # permission check when create
        return request.user.is_staff or request.user.is_roomer


class SafelistPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        remote_addr = request.META['REMOTE_ADDR']
        for valid_ip in settings.SAFE_IPS:
            if remote_addr == valid_ip or remote_addr.startswith(valid_ip):
                logger.info(f'request from {remote_addr} is allowed')
                return True
        else:
            logger.info(f'request from {remote_addr} is NOT allowed')

        return False
