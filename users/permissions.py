from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверка на принадлежность к группе модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="admins").exists()


class IsOwner(permissions.BasePermission):
    """Проверка на владельа задачи"""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
