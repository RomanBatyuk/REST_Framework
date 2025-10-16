from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import Payment, User
from django_countries import countries


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class UserSerializer(ModelSerializer):
    country = serializers.ChoiceField(choices=countries, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = "__all__"