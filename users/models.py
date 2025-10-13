from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


###### Создан пользователь 1: ID 1, Email: user1@example.com, password='password123'
###### Создан пользователь 2: ID 2, Email: user2@example.com, password='password456'


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон", help_text="Укажите номер теелфона")
    country = CountryField(blank_label="Страна не выбрана", blank=True, null=True)
    avatar = models.ImageField(upload_to="users/avatars", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите аватар")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

User = get_user_model()  # Получаем модель пользователя

class Payment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, который совершил оплату"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
        help_text="Дата и время совершения оплаты"
    )
    paid_course = models.ForeignKey(
        "materials.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
        help_text="Курс, за который произведена оплата (если оплата за курс)"
    )
    paid_lesson = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок",
        help_text="Урок, за который произведена оплата (если оплата за урок)"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Сумма оплаты в рублях (например, 1500.00)"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Наличные'),
            ('transfer', 'Перевод на счет'),
        ],
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты"
    )

    def clean(self):
        super().clean()
        # Проверяем, что заполнено ровно одно из полей
        if not (self.paid_course or self.paid_lesson):
            raise ValidationError("Должен быть указан оплаченный курс или урок.")
        if self.paid_course and self.paid_lesson:
            raise ValidationError("Нельзя указывать и курс, и урок одновременно.")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платеж от {self.user} на сумму {self.amount} ({self.payment_method})"
