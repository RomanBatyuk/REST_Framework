from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from users.views import PaymentViewSet, UserCreateAPIView, UserRetrieveAPIView, UserDestroyAPIView, UserUpdateAPIView
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),

    path('register/', UserCreateAPIView.as_view(), name='register'),
    path("user/<int:pk>/", UserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("user/<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user_delete"),
    path("user/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user_update"),
] + router.urls
