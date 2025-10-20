from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="user1@email.ru")
        self.course = Course.objects.create(name="Первый курс", owner=self.user)
        self.lesson = Lesson.objects.create(name="Урок первый", course=self.course, owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        """Тест просмотра урока."""
        url = reverse("materials:lesson_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], "Урок первый")

    def test_lesson_create(self):
        """Тест создания урока."""
        url = reverse("materials:lesson_create")
        data = {
        "video_url": "https://www.Youtube.com/watch?v=abc",
        "name": "Урок первый",
        "description": "Простое описание",
        "course": self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        """Тест обновления данных в уроке."""
        url = reverse("materials:lesson_update", args=(self.lesson.pk,))
        data = {
        "name": "Урок второй"
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Урок второй")

    def test_lesson_delete(self):
        """Тест удаления урока."""
        url = reverse("materials:lesson_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        """Тест вывода списка уроков."""
        url = reverse("materials:lesson_list")
        response = self.client.get(url)
        data = response.json()  # Вызов метода!
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], "Урок первый")


class SubscriptionViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="testuser@example.com", password="password123")
        self.course = Course.objects.create(name="Тестовый курс", owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_subscribe_to_course(self):
        """Тест успешной подписки на курс."""
        url = reverse('course:subscribe', args=(self.course.pk,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("оформлена", response.data['message'])
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Тест отмены подписки (если уже подписан)."""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('course:subscribe', args=(self.course.pk,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("отменена", response.data['message'])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_not_found(self):
        """Тест попытки подписки на несуществующий курс."""
        non_existent_course_id = 9999
        url = reverse('course:subscribe', args=(non_existent_course_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("не найден", response.data['error'])

    def test_unauthenticated_access(self):
        """Тест доступа без аутентификации."""
        self.client.logout()
        url = reverse('course:subscribe', args=(self.course.pk,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
