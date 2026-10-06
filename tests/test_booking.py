"""Tests for slot generation and booking."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import AvailabilityRule, BlockedSlot, Booking, Student
from bookings.services.booking import (
    PublicBookingData,
    SlotCollisionError,
    create_public_booking,
)
from bookings.services.slots import TimeSlot, get_available_slots
from organizations.models import Organization, Teacher

User = get_user_model()


class BookingTestCase(TestCase):
    """Base fixtures for booking tests."""

    def setUp(self):
        self.user = User.objects.create_user(email="teacher@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="Test School",
            slug="test-school",
            contact_email="teacher@test.com",
            timezone="Europe/Moscow",
            slot_duration_minutes=60,
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Test Teacher",
        )
        AvailabilityRule.objects.create(
            teacher=self.teacher,
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )


class SlotGenerationTests(BookingTestCase):
    def test_generates_hourly_slots(self):
        tz = ZoneInfo("Europe/Moscow")
        # Next Monday
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        monday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.teacher, monday)
        self.assertEqual(len(slots), 2)
        self.assertEqual(
            (slots[1].starts_at - slots[0].starts_at).total_seconds(),
            3600,
        )

    def test_booked_slot_excluded(self):
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)

        student = Student.objects.create(
            organization=self.org,
            parent_name="Parent",
            parent_email="parent@test.com",
            parent_phone="+79990001122",
            child_name="Child",
            child_age=10,
        )
        Booking.objects.create(
            organization=self.org,
            teacher=self.teacher,
            student=student,
            starts_at=slots[0].starts_at,
            ends_at=slots[0].ends_at,
            status=Booking.Status.PENDING,
        )

        slots_after = get_available_slots(self.teacher, monday)
        self.assertEqual(len(slots_after), len(slots) - 1)

    def test_blocked_slot_excluded(self):
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)

        BlockedSlot.objects.create(
            teacher=self.teacher,
            starts_at=slots[0].starts_at,
            ends_at=slots[0].ends_at,
            reason="Отпуск",
        )

        slots_after = get_available_slots(self.teacher, monday)
        self.assertEqual(len(slots_after), len(slots) - 1)
        self.assertNotIn(slots[0], slots_after)


class BookingServiceTests(BookingTestCase):
    def _next_monday_slot(self) -> TimeSlot:
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)
        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots, "Expected at least one slot")
        return slots[0]

    def test_create_public_booking(self):
        slot = self._next_monday_slot()
        data = PublicBookingData(
            parent_name="Иван",
            parent_email="ivan@test.com",
            parent_phone="+79990001122",
            child_name="Петя",
            child_age=9,
            notes="",
        )
        booking = create_public_booking(self.org, self.teacher, slot, data)
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.student.status, Student.Status.NEW)
        self.assertEqual(len(mail.outbox), 2)

    def test_double_booking_raises_collision(self):
        slot = self._next_monday_slot()
        data = PublicBookingData(
            parent_name="Иван",
            parent_email="ivan@test.com",
            parent_phone="+79990001122",
            child_name="Петя",
            child_age=9,
            notes="",
        )
        create_public_booking(self.org, self.teacher, slot, data)
        with self.assertRaises(SlotCollisionError):
            create_public_booking(self.org, self.teacher, slot, data)


class PublicFormTests(BookingTestCase):
    def test_public_booking_form_submission(self):
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)
        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)

        client = Client()
        url = reverse("public:book", kwargs={"slug": self.org.slug})
        response = client.post(url, {
            "parent_name": "Мария",
            "parent_email": "maria@test.com",
            "parent_phone": "+79990003344",
            "child_name": "Саша",
            "child_age": 11,
            "notes": "Пробный урок",
            "slot_start": slots[0].starts_at.isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заявка отправлена")
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)


class RateLimitTests(BookingTestCase):
    def test_rate_limit_blocks_excessive_posts(self):
        from django.test import override_settings

        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)
        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)

        client = Client()
        url = reverse("public:book", kwargs={"slug": self.org.slug})
        payload = {
            "parent_name": "Мария",
            "parent_email": "maria@test.com",
            "parent_phone": "+79990003344",
            "child_name": "Саша",
            "child_age": 11,
            "notes": "",
            "slot_start": slots[0].starts_at.isoformat(),
        }

        with override_settings(PUBLIC_BOOKING_RATE_LIMIT=1):
            client.post(url, payload)
            response = client.post(url, payload)
            self.assertEqual(response.status_code, 429)


class AuthTests(TestCase):
    def test_registration_creates_org_and_teacher(self):
        client = Client()
        response = client.post(reverse("accounts:register"), {
            "email": "new@school.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "organization_name": "Новая школа",
            "teacher_name": "Ольга",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@school.com").exists())
        user = User.objects.get(email="new@school.com")
        self.assertTrue(hasattr(user, "teacher_profile"))
        self.assertEqual(user.teacher_profile.organization.name, "Новая школа")
