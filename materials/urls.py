from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.views import CourseViewSet, LessonListAPIView, LessonCreateAPIView, LessonUpdateAPIView, \
    LessonRetrieveAPIView, LessonDestroyAPIView, SubscriptionView, Course_purchaseCreateAPIView
from materials.apps import MaterialsConfig

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lesson/", LessonListAPIView.as_view(), name="lesson_list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson_retrieve"),
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson_create"),
    path("lesson/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson_delete"),
    path("lesson/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson_update"),
    path('subscribe/<int:course_id>/', SubscriptionView.as_view(), name='subscribe'),
    path("CoursePurchase/", Course_purchaseCreateAPIView.as_view(), name="CoursePurchase")

]

urlpatterns += router.urls