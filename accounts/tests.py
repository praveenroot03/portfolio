from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import UserMFA
from .totp import totp_at


class MFAAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

    def _create_user(self, username="admin", password="p455w0rd"):
        user = self.User.objects.create_user(
            username=username,
            password=password,
            is_staff=True,
            is_superuser=True,
            email="admin@example.com",
        )
        return user, password

    def test_login_requires_token_when_mfa_enabled(self):
        user, password = self._create_user()
        mfa = UserMFA.objects.create(user=user)

        login_url = reverse("admin:login")
        response = self.client.post(
            login_url,
            {"username": user.username, "password": password},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "One-time code")
        self.assertContains(response, "Enter the code from your authenticator app")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        response = self.client.post(
            login_url,
            {
                "username": user.username,
                "password": password,
                "token": totp_at(mfa.secret),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(str(user.pk), self.client.session.get("_auth_user_id"))

        mfa.refresh_from_db()
        self.assertIsNotNone(mfa.last_verified)

    def test_login_without_mfa_skips_token(self):
        user, password = self._create_user(username="other")

        login_url = reverse("admin:login")
        response = self.client.post(
            login_url,
            {"username": user.username, "password": password},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(str(user.pk), self.client.session.get("_auth_user_id"))
