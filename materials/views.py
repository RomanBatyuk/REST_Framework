from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsNotModerator, IsModeratorOrOwner, IsNotModeratorOrOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsNotModerator]
        elif self.action in ["update", "retrieve"]:
            permission_classes = [IsModeratorOrOwner]
        elif self.action == "destroy":
            permission_classes = [IsNotModeratorOrOwner]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        # Для list: пустой список (как в CourseViewSet для else)
        permission_classes = []
        return [permission() for permission in permission_classes]

class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Для create: IsNotModerator
        permission_classes = [IsNotModerator]
        return [permission() for permission in permission_classes]

class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsNotModeratorOrOwner]
        return [permission() for permission in permission_classes]
