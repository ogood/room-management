from rest_framework import permissions
class OwnerInRole(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_permission(self, request, view):
        return True
    def has_object_permission(self, request, view, obj):#check when get single object
        return True

class ObjectOwnerMatch(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_permission(self, request, view):

        # Write permissions are only allowed to the owner of the snippet.
        return True

    def has_object_permission(self, request, view, obj):#check when get single object
        if request.user.is_superuser:
            return True
        try:
            return request.user == obj.owner#it's a parent product
        except AttributeError:
            return request.user == obj.parent.owner#it's a child product

class ParentOwnerMatch(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_permission(self, request, view):

        # Write permissions are only allowed to the owner of the snippet.
        return True

    def has_object_permission(self, request, view, obj):#check when get single object
        if request.user.is_superuser:
            return True
        try:
            return request.user == obj.owner#it's a parent product
        except AttributeError:
            return request.user == obj.parent.owner#it's a child product