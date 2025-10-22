from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view




@extend_schema_view(
    list=extend_schema(
        summary="Список платежей",
        description="Возвращает список всех платежей с пагинацией, фильтрацией по 'paid_course', 'paid_lesson', 'payment_method' и сортировкой по 'payment_date'. Доступно аутентифицированным пользователям.",
        responses={
            200: PaymentSerializer(many=True),
            401: None,
        },
        tags=['Payments']
    ),
    create=extend_schema(
        summary="Создать платёж",
        description="Создаёт новый платёж. Требуется аутентификация.",
        request=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: None,  # Ошибки валидации
            401: None,
        },
        tags=['Payments']
    ),
    retrieve=extend_schema(
        summary="Детали платежа",
        description="Возвращает подробности конкретного платежа. Доступно аутентифицированным пользователям.",
        responses={
            200: PaymentSerializer,
            401: None,
            404: None,  # Платёж не найден
        },
        tags=['Payments']
    ),
    update=extend_schema(
        summary="Обновить платёж",
        description="Обновляет существующий платёж. Доступно аутентифицированным пользователям.",
        request=PaymentSerializer,
        responses={
            200: PaymentSerializer,
            400: None,
            401: None,
            404: None,
        },
        tags=['Payments']
    ),
    destroy=extend_schema(
        summary="Удалить платёж",
        description="Удаляет платёж. Доступно аутентифицированным пользователям.",
        responses={
            204: None,  # Успешное удаление
            401: None,
            404: None,
        },
        tags=['Payments']
    )
)
class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]  # Поля для фильтрации
    ordering_fields = ["payment_date"]  # Поле для сортировки

@extend_schema(
    summary="Создать пользователя",
    description="Регистрирует нового пользователя. Доступно всем (без аутентификации).",
    request=UserSerializer,
    responses={
        201: UserSerializer,
        400: None,  # Ошибки валидации
    },
    tags=['Users']
)
class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

@extend_schema(
    summary="Обновить пользователя",
    description="Обновляет профиль пользователя. Доступно только аутентифицированным пользователям (для своего профиля).",
    request=UserSerializer,
    responses={
        200: UserSerializer,
        400: None,
        401: None,
        403: None,  # Запрещено (не свой профиль)
        404: None,
    },
    tags=['Users']
)
class UserUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(
    summary="Детали пользователя",
    description="Возвращает подробности пользователя. Доступно только аутентифицированным пользователям (для своего профиля).",
    responses={
        200: UserSerializer,
        401: None,
        403: None,
        404: None,
    },
    tags=['Users']
)
class UserRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(
    summary="Удалить пользователя",
    description="Удаляет профиль пользователя. Доступно только аутентифицированным пользователям (для своего профиля).",
    responses={
        204: None,
        401: None,
        403: None,
        404: None,
    },
    tags=['Users']
)
class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
