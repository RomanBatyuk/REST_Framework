from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from materials.models import Course, Lesson, Subscription, Course_purchase
from materials.paginators import PaginationList
from materials.serializers import CourseSerializer, LessonSerializer, Course_purchaseSerializer
from materials.services import create_stripe_price, create_stripe_session
from users.permissions import IsNotModerator, IsModeratorOrOwner, IsNotModeratorOrOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view
from materials.tasks import send_course_update_notification


@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Возвращает список всех курсов с пагинацией. Доступно всем пользователям.",
        responses={
            200: CourseSerializer(many=True),
        },
        tags=['Courses']
    ),
    create=extend_schema(
        summary="Создать курс",
        description="Создаёт новый курс. Требуется аутентификация. Только могут создавать все, кроме модераторов.",
        request=CourseSerializer,
        responses={
            201: CourseSerializer,
            400: None,  # Ошибки валидации
            401: None,  # Не аутентифицирован
            403: None,  # Запрещено (не-модератор)
        },
        tags=['Courses']
    ),
    retrieve=extend_schema(
        summary="Детали курса",
        description="Возвращает подробности конкретного курса. Доступно модераторам или владельцу.",
        responses={
            200: CourseSerializer,
            401: None,
            403: None,
            404: None,  # Курс не найден
        },
        tags=['Courses']
    ),
    update=extend_schema(
        summary="Обновить курс",
        description="Обновляет существующий курс. Доступно модераторам или владельцу. После обновления автоматически"
                    "отправляются асинхронные email-уведомления подписчикам о изменениях материалов.",
        request=CourseSerializer,
        responses={
            200: CourseSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
        },
        tags=['Courses']
    ),
    destroy=extend_schema(
        summary="Удалить курс",
        description="Удаляет курс. Доступно всем кроме модераторов.",
        responses={
            204: None,
            401: None,
            403: None,
            404: None,
        },
        tags=['Courses']
    )
)

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # Сохраняет изменения

        # Асинхронно отправляем уведомления подписчикам после обновления
        send_course_update_notification.delay(instance.id)

        if getattr(instance, '_prefetched_objects_cache', None):
            # Populate prefetched object cache after updating.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(  # Декоратор для описания схемы
        summary="Управление подпиской на курс",  # Краткое описание
        description="Создаёт или удаляет подписку на курс. Если подписка существует — удаляет, иначе создаёт.",
        request=None,  # Нет тела запроса (POST без данных)
        responses={
            201: {"description": "Подписка оформлена"},
            200: {"description": "Подписка отменена"},
            # 401: {"description": "Не аутентифицирован"},
            404: {"description": "Курс не найден"},
        },
    )

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

@extend_schema(
    summary="Список уроков",
    description="Возвращает список всех уроков с пагинацией. Доступно всем пользователям.",
    responses={
        200: LessonSerializer(many=True),
    },
    tags=['Lessons']
)
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

@extend_schema(
    summary="Создать урок",
    description="Создаёт новый урок. Требуется аутентификация. Могут создавать все кроме модераторов.",
    request=LessonSerializer,
    responses={
        201: LessonSerializer,
        400: None,
        401: None,
        403: None,
    },
    tags=['Lessons']
)
class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        permission_classes = [IsNotModerator]
        return [permission() for permission in permission_classes]

@extend_schema(
    summary="Обновить урок",
    description="Обновляет существующий урок. Доступно модераторам или владельцу.",
    request=LessonSerializer,
    responses={
        200: LessonSerializer,
        400: None,
        401: None,
        403: None,
        404: None,
    },
    tags=['Lessons']
)
class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

@extend_schema(
    summary="Детали урока",
    description="Возвращает подробности конкретного урока. Доступно модераторам или владельцу.",
    responses={
        200: LessonSerializer,
        401: None,
        403: None,
        404: None,
    },
    tags=['Lessons']
)
class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

@extend_schema(
    summary="Удалить урок",
    description="Удаляет урок. Доступно всем кроме модераторов.",
    responses={
        204: None,
        401: None,
        403: None,
        404: None,
    },
    tags=['Lessons']
)
class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        permission_classes = [IsNotModeratorOrOwner]
        return [permission() for permission in permission_classes]


class Course_purchaseCreateAPIView(CreateAPIView):
    queryset = Course_purchase.objects.all()
    serializer_class = Course_purchaseSerializer

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        price = create_stripe_price(payment)
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.link = payment_link
        payment.save()
