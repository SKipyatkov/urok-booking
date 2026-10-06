"""Sprint 7 tests: landing, stats, CSV export, slug editing."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, Student
from organizations.models import Organization, Teacher

User = get_user_model()


class Sprint7TestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="t7@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="School 7",
            slug="school-7",
            contact_email="t7@test.com",
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Teacher 7",
        )
        self.client = Client()
        self.client.login(email="t7@test.com", password="pass12345")

        Student.objects.create(
            organization=self.org,
            parent_name="P",
            parent_email="p@test.com",
            parent_phone="+79990001122",
            child_name="Kid",
            child_age=10,
            status=Student.Status.NEW,
        )
        student2 = Student.objects.create(
            organization=self.org,
            parent_name="P2",
            parent_email="p2@test.com",
            parent_phone="+79990001123",
            child_name="Kid2",
            child_age=11,
            status=Student.Status.ACTIVE,
        )
        Booking.objects.create(
            organization=self.org,
            teacher=self.teacher,
            student=student2,
            starts_at=timezone.now() + timedelta(days=2),
            ends_at=timezone.now() + timedelta(days=2, hours=1),
            status=Booking.Status.PENDING,
        )


class LandingTests(TestCase):
    def test_guest_sees_landing(self):
        response = Client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Запись на уроки без хаоса")
        self.assertContains(response, "Попробовать бесплатно")

    def test_authenticated_redirects_to_cabinet(self):
        user = User.objects.create_user(email="auth@test.com", password="pass12345")
        org = Organization.objects.create(
            name="Auth",
            slug="auth",
            contact_email="auth@test.com",
            trial_ends_at=Organization.default_trial_end(),
        )
        Teacher.objects.create(organization=org, user=user, name="T")
        client = Client()
        client.login(email="auth@test.com", password="pass12345")
        response = client.get("/")
        self.assertRedirects(response, reverse("cabinet:dashboard"))


class DashboardStatsTests(Sprint7TestCase):
    def test_dashboard_shows_stats(self):
        response = self.client.get(reverse("cabinet:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новые ученики")
        self.assertContains(response, "Ожидают подтверждения")


class CsvExportTests(Sprint7TestCase):
    def test_students_csv_download(self):
        response = self.client.get(reverse("cabinet:students_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("students.csv", response["Content-Disposition"])
        self.assertIn("Kid", response.content.decode("utf-8-sig"))

    def test_bookings_csv_download(self):
        response = self.client.get(reverse("cabinet:bookings_export"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("bookings.csv", response["Content-Disposition"])


class SlugEditTests(Sprint7TestCase):
    def test_slug_can_be_changed(self):
        response = self.client.post(reverse("cabinet:settings"), {
            "name": self.org.name,
            "slug": "new-slug-7",
            "description": "",
            "contact_email": self.org.contact_email,
            "timezone": self.org.timezone,
            "slot_duration_minutes": self.org.slot_duration_minutes,
        })
        self.assertRedirects(response, reverse("cabinet:settings"))
        self.org.refresh_from_db()
        self.assertEqual(self.org.slug, "new-slug-7")
