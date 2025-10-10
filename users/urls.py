from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import PaymentViewSet
from users.apps import UsersConfig

app_name = UsersConfig.name

router = SimpleRouter()
router.register("payments", PaymentViewSet)

urlpatterns = router.urls