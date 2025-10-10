from rest_framework.viewsets import ModelViewSet
from users.models import Payment
from users.serializers import PaymentSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]  # Поля для фильтрации
    ordering_fields = ["payment_date"]  # Поле для сортировки