from __future__ import annotations

from datetime import timedelta
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from mainPage.log import VisitorLogger
from mainPage.models import (
    Background_img,
    About,
    Blog,
    Contact,
    People,
    Portfolio,
    Specialisation,
    Visit_detail,
)
from mainPage.utils import Utility


def _build_image_file(name: str = "test.jpg") -> SimpleUploadedFile:
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - Pillow is required by the app.
        raise AssertionError("Pillow must be installed for tests to run.")

    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/{name}"
        image = Image.new("RGB", (10, 10), color="blue")
        image.save(path, format="JPEG")
        with open(path, "rb") as handle:
            data = handle.read()

    return SimpleUploadedFile(name, data, content_type="image/jpeg")


class UtilityTests(TestCase):
    def setUp(self) -> None:
        self.utility = Utility()
        self.factory = RequestFactory()

    def test_get_client_ip_address_prefers_forwarded_header(self) -> None:
        request = self.factory.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.5, 198.51.100.1"

        self.assertEqual(self.utility.get_client_ip_address(request), "203.0.113.5")

    def test_get_client_ip_address_falls_back_to_remote_addr(self) -> None:
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "192.0.2.10"

        self.assertEqual(self.utility.get_client_ip_address(request), "192.0.2.10")

    def test_get_user_agent_returns_meta_value(self) -> None:
        request = self.factory.get("/")
        request.META["HTTP_USER_AGENT"] = "TestAgent/1.0"

        self.assertEqual(self.utility.get_user_agent(request), "TestAgent/1.0")


class VisitorLoggerTests(TestCase):
    def setUp(self) -> None:
        self.logger = VisitorLogger()

    def _patch_location(self):
        return patch("mainPage.models.Utility.get_location_via_ip", return_value=None)

    def test_add_creates_people_and_visit_detail(self) -> None:
        with self._patch_location():
            self.logger.add(
                "203.0.113.5",
                "TestAgent/1.0",
                feedback={"name": "Alice", "email": "alice@example.com", "message": "Hi"},
            )

        person = People.objects.get()
        detail = Visit_detail.objects.get()

        self.assertEqual(person.ip_address, "203.0.113.5")
        self.assertEqual(person.no_of_visits, 1)
        self.assertEqual(detail.email_id, "alice@example.com")
        self.assertEqual(detail.message, "Hi")

    def test_add_increments_visits_after_cooldown(self) -> None:
        stale_time = timezone.now() - (VisitorLogger.cooldown + timedelta(minutes=1))
        person = People.objects.create(
            ip_address="198.51.100.4", no_of_visits=1, last_visited=stale_time
        )

        with self._patch_location():
            self.logger.add("198.51.100.4", "TestAgent/2.0")

        person.refresh_from_db()
        self.assertEqual(person.no_of_visits, 2)
        self.assertGreaterEqual(person.last_visited, stale_time)

    def test_add_does_not_increment_visits_within_cooldown(self) -> None:
        recent_time = timezone.now()
        person = People.objects.create(
            ip_address="192.0.2.44", no_of_visits=3, last_visited=recent_time
        )

        with self._patch_location():
            self.logger.add("192.0.2.44", "TestAgent/3.0")

        person.refresh_from_db()
        self.assertEqual(person.no_of_visits, 3)
        self.assertGreaterEqual(person.last_visited, recent_time)


class SpecialisationTests(TestCase):
    def setUp(self) -> None:
        self.portfolio = Portfolio.objects.create(title_text="Title", name_content="Name")

    def test_saving_more_than_three_specialisations_is_prevented(self) -> None:
        Specialisation.objects.create(portfolio=self.portfolio, specialisation_name="One")
        Specialisation.objects.create(portfolio=self.portfolio, specialisation_name="Two")
        Specialisation.objects.create(portfolio=self.portfolio, specialisation_name="Three")

        with self.assertRaisesMessage(ValidationError, "Only three specialisation allowed"):
            Specialisation.objects.create(portfolio=self.portfolio, specialisation_name="Four")

    def test_updating_existing_specialisation_is_allowed(self) -> None:
        spec = Specialisation.objects.create(
            portfolio=self.portfolio, specialisation_name="Initial"
        )

        spec.specialisation_name = "Updated"
        spec.save()

        self.assertEqual(Specialisation.objects.get(pk=spec.pk).specialisation_name, "Updated")


class BackgroundImageTests(TestCase):
    def setUp(self) -> None:
        self.portfolio = Portfolio.objects.create(title_text="Title", name_content="Name")

    def test_random_returns_none_when_no_backgrounds(self) -> None:
        self.assertIsNone(Background_img.random())

    def test_random_returns_image_when_available(self) -> None:
        image = _build_image_file()
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            Background_img.objects.create(portfolio=self.portfolio, image=image)

            random_background = Background_img.random()

        self.assertIsNotNone(random_background)


class IndexViewTests(TestCase):
    def setUp(self) -> None:
        self.portfolio = Portfolio.objects.create(title_text="Title", name_content="Name")
        self.about = About.objects.create(image=_build_image_file(), content="Line one\nLine two")
        Blog.objects.create(title="Post", pub_date=timezone.now(), link="https://example.com")
        Contact.objects.create(types="fa-linkedin", link="https://linkedin.example")

    def test_index_get_logs_visit_without_feedback(self) -> None:
        with patch("mainPage.models.Utility.get_location_via_ip", return_value=None):
            response = self.client.get(reverse("mainPage:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(People.objects.filter(ip_address="127.0.0.1").exists())
        self.assertEqual(Visit_detail.objects.count(), 1)


class ServeImageViewTests(TestCase):
    def setUp(self) -> None:
        self.portfolio = Portfolio.objects.create(title_text="Title", name_content="Name")

    def test_serve_image_returns_404_for_missing_background(self) -> None:
        response = self.client.get(reverse("mainPage:serve_image", args=["bg"]))
        self.assertEqual(response.status_code, 404)

    def test_serve_image_returns_file_for_background(self) -> None:
        image = _build_image_file()
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            Background_img.objects.create(portfolio=self.portfolio, image=image)

            response = self.client.get(reverse("mainPage:serve_image", args=["bg"]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
