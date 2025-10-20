from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import validate_forbidden_reference


class LessonSerializer(ModelSerializer):
    video_url = serializers.URLField(validators=[validate_forbidden_reference])

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ['owner']

class CourseSerializer(ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = ("id", "name", "description", "lessons_count", "is_subscribed", "owner", "lessons")

    def get_is_subscribed(self, obj):
        # Получаем текущего пользователя из контекста запроса
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем, есть ли подписка на этот курс для пользователя
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False  # Если пользователь не аутентифицирован



