from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from materials.models import Course, Lesson, Subscription
from materials.paginators import PaginationList
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsNotModerator, IsModeratorOrOwner, IsNotModeratorOrOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
# from django.shortcuts import get_object_or_404


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = PaginationList

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

    def get(self, request):
        queryset = Course.objects.all()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = CourseSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):  # Добавляем course_id как параметр
        user = request.user

        # Проверяем, существует ли курс
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли уже подписка
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={}  # Ничего не устанавливаем, если создаём
        )

        if not created:
            # Если подписка уже существует, удаляем её (toggle-логика)
            subscription.delete()
            return Response({"message": f"Подписка на курс '{course.name}' отменена."}, status=status.HTTP_200_OK)
        else:
            # Если создана новая подписка
            return Response({"message": f"Подписка на курс '{course.name}' оформлена."},
                            status=status.HTTP_201_CREATED)


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = PaginationList

    def get_permissions(self):
        permission_classes = []
        return [permission() for permission in permission_classes]

    def get(self, request):
        queryset = Lesson.objects.all()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = LessonSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
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
