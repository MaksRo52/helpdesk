from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Task

User = get_user_model()


class TaskListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.superuser = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.task1 = Task.objects.create(title="Task 1", author=self.user, status="new")
        self.task2 = Task.objects.create(
            title="Task 2", author=self.user, status="work"
        )
        self.url = reverse("main:index")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={self.url}")

    def test_list_tasks_for_logged_in_user(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")

    def test_list_tasks_with_status_filter(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url, {"status": "new"})
        self.assertContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")

    def test_list_tasks_for_superuser(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(self.url)
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")


class TaskDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.task = Task.objects.create(title="Task 1", author=self.user, status="new")
        self.url = reverse("main:task_detail", args=[self.task.pk])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={self.url}")

    def test_view_task_detail(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")


class TaskCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("main:task_create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('users:login')}?redirect_to={self.url}"
        )

    def test_create_task(self):
        self.client.login(username="testuser", password="password")
        data = {
            "title": "New Task",
            "description": "Task description",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation
        self.assertTrue(Task.objects.filter(title="New Task").exists())


class TaskUpdateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.task = Task.objects.create(title="Task 1", author=self.user, status="new")
        self.url = reverse("main:task_update", args=[self.task.pk])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={self.url}")

    def test_update_task(self):
        self.client.login(username="testuser", password="password")
        data = {
            "title": "Updated Task",
            "description": "Updated description",
            "status": "work",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")


class TaskAtWorkTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.task = Task.objects.create(title="Task 1", author=self.user, status="new")
        self.url = reverse("main:task_at_work", args=[self.task.pk])

    def test_change_task_status_to_work(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "work")
        self.assertEqual(self.task.executor, self.user)


class TaskCloseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.task = Task.objects.create(title="Task 1", author=self.user, status="work")
        self.url = reverse("main:task_close", args=[self.task.pk])

    def test_change_task_status_to_complete(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "complete")
