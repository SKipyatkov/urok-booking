"""Sprint 2 tests: forms, cabinet, rate limit edge cases."""

from datetime import UTC, datetime, time, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from bookings.forms import DatePickerForm
from bookings.models import AvailabilityRule, Booking, Student
from bookings.services.slots import get_available_slots
from organizations.models import Organization, Teacher

User = get_user_model()


class DatePickerFormTests(TestCase):
    @patch("django.utils.timezone.now")
    def test_rejects_yesterday_in_moscow_when_utc_still_previous_day(self, mock_now):
        # 22:00 UTC on Jul 12 = 01:00 Moscow on Jul 13
        mock_now.return_value = datetime(2026, 7, 12, 22, 0, tzinfo=UTC)

        yesterday_form = DatePickerForm({"date": "2026-07-12"}, tz_name="Europe/Moscow")
        self.assertFalse(yesterday_form.is_valid())
        self.assertIn("прошедшую", yesterday_form.errors["date"][0].lower())

        today_form = DatePickerForm({"date": "2026-07-13"}, tz_name="Europe/Moscow")
        self.assertTrue(today_form.is_valid())


class CabinetBookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="teacher@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="Test School",
            slug="test-school",
            contact_email="teacher@test.com",
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Test Teacher",
        )
        self.student = Student.objects.create(
            organization=self.org,
            parent_name="Parent",
            parent_email="parent@test.com",
            parent_phone="+79990001122",
            child_name="Child",
            child_age=10,
        )
        self.booking = Booking.objects.create(
            organization=self.org,
            teacher=self.teacher,
            student=self.student,
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=1),
            status=Booking.Status.PENDING,
        )
        self.client = Client()
        self.client.login(username="teacher@test.com", password="pass12345")

    def test_booking_detail_post_updates_status_and_meeting_url(self):
        url = reverse("cabinet:booking_detail", kwargs={"pk": self.booking.pk})
        response = self.client.post(url, {
            "status": Booking.Status.CONFIRMED,
            "meeting_url": "https://telemost.yandex.ru/j/12345",
        })
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)
        self.assertEqual(self.booking.meeting_url, "https://telemost.yandex.ru/j/12345")


class RateLimitFormTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(email="t2@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="School 2",
            slug="school-2",
            contact_email="t2@test.com",
            timezone="Europe/Moscow",
            slot_duration_minutes=60,
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Teacher 2",
        )
        AvailabilityRule.objects.create(
            teacher=self.teacher,
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

    def test_invalid_form_does_not_consume_rate_limit(self):
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)
        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)

        client = Client()
        url = reverse("public:book", kwargs={"slug": self.org.slug})
        invalid = {
            "parent_name": "Мария",
            "parent_email": "maria@test.com",
            "parent_phone": "+79990003344",
            "child_name": "Саша",
            "child_age": 11,
            "notes": "",
            "slot_start": "",
        }
        valid = {**invalid, "slot_start": slots[0].starts_at.isoformat()}

        with override_settings(PUBLIC_BOOKING_RATE_LIMIT=1):
            for _ in range(3):
                response = client.post(url, invalid)
                self.assertEqual(response.status_code, 400)

            response = client.post(url, valid)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Заявка отправлена")

            response = client.post(url, valid)
            self.assertEqual(response.status_code, 429)
