from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountFlowTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "ivan",
                "email": "ivan@example.com",
                "password1": "Stalingram-test-1945",
                "password2": "Stalingram-test-1945",
            },
        )
        self.assertRedirects(response, reverse("messenger:home"))
        self.assertTrue(User.objects.filter(username="ivan", email="ivan@example.com").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="ivan").pk)

    def test_login_accepts_username(self):
        User.objects.create_user("zhukov", "zhukov@example.com", "Stalingram-test-1945")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "zhukov", "password": "Stalingram-test-1945"},
        )
        self.assertRedirects(response, reverse("messenger:home"))

    def test_login_accepts_email(self):
        User.objects.create_user("rokossovsky", "marshal@example.com", "Stalingram-test-1945")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "marshal@example.com", "password": "Stalingram-test-1945"},
        )
        self.assertRedirects(response, reverse("messenger:home"))

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user("first", "user@example.com", "Stalingram-test-1945")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "second",
                "email": "USER@example.com",
                "password1": "Stalingram-test-1945",
                "password2": "Stalingram-test-1945",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Эта почта уже используется.")
