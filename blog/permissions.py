from rest_framework import permissions


class FaqatMuallifOzgartiradi(permissions.BasePermission):
    """Postni faqat uning muallifi o'zgartirishi yoki o'chirishi mumkin."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.muallif == request.user