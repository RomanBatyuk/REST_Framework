from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название курса", help_text="Введите название курса")
    image = models.ImageField(upload_to="users/image", blank=True, null=True, verbose_name="Картинка", help_text="Загрузите картинку")
    description = models.TextField(blank=True, null=True, verbose_name="Описание", help_text="Введите описание")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"



class Lesson(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название урока", help_text="Введите название урока")
    image = models.ImageField(upload_to="users/image", blank=True, null=True, verbose_name="Картинка", help_text="Загрузите картинку")
    description = models.TextField(blank=True, null=True, verbose_name="Описание", help_text="Введите описание урока")
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на урок", help_text="Введите ссылку на видео")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name="Пользователь")
    course = models.ForeignKey("materials.Course", on_delete=models.CASCADE, verbose_name="Курс")

    class Meta:
        unique_together = ('user', 'course')
