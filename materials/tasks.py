from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from materials.models import Course, Subscription
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_course_update_notification(course_id):
    """
    Асинхронная задача: отправляет email всем подписчикам курса о обновлении материалов.
    """
    try:
        course = Course.objects.get(id=course_id)
        # Получаем emails подписчиков (только активных, без дубликатов)
        subscribers_emails = Subscription.objects.filter(
            course=course
        ).select_related('user').values_list('user__email', flat=True).distinct()


        subject = f"Обновление материалов курса: {course.name}"
        message = f"""Привет! Материалы курса "{course.name}" были обновлены.
        Заходите проверить новые материалы: {settings.SITE_URL}/course/{course.id}/
        """

        for email in subscribers_emails:
            if email:  # Проверяем, что email не пустой
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

        print(f"Уведомления отправлены {len(subscribers_emails)} подписчикам курса {course.name}")

    except Course.DoesNotExist:
        print(f"Курс с ID {course_id} не найден — рассылка пропущена.")
    except Exception as e:
        print(f"Ошибка при отправке уведомлений для курса {course_id}: {e}")


@shared_task
def check_inactive_users():
    cutoff_date = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=cutoff_date, is_active=True)
    count = inactive_users.update(is_active=False)
    return f'Заблокировано {count} пользователей'
