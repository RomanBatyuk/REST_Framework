from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView


class IsModerator(permissions.BasePermission):
    """Проверяте являестя ли пользователь модератором."""

    message = "Вы не являетесь модератором."

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Moderator").exists()


class IsOwner(permissions.BasePermission):
    """Проверяте являестя ли пользователь владельцем."""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsModeratorOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        action = getattr(view, 'action', None)
        if action is None:
            if isinstance(view, ListAPIView):
                action = 'list'
            elif isinstance(view, CreateAPIView):
                action = 'create'
            elif isinstance(view, RetrieveAPIView):
                action = 'retrieve'
            elif isinstance(view, UpdateAPIView):
                action = 'update'
            elif isinstance(view, DestroyAPIView):
                action = 'destroy'


        if action == 'list':
            return IsModerator().has_permission(request, view)
        elif action in ['retrieve', 'update']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return IsModerator().has_object_permission(request, view, obj) or IsOwner().has_object_permission(request, view,
                                                                                                          obj)


class IsNotModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return not IsModerator().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return not IsModerator().has_object_permission(request, view, obj)


class IsNotModeratorOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return IsNotModerator().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return IsNotModerator().has_object_permission(request, view, obj) or IsOwner().has_object_permission(request,
                                                                                                             view, obj)