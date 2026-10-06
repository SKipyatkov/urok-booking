"""Sprint 10: logo WebP, student dedup, UI helpers."""

from datetime import time, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils import timezone

from bookings.models import AvailabilityRule, Booking, Student
from bookings.services.booking import PublicBookingData, create_public_booking
from bookings.services.slots import get_available_slots
from bookings.templatetags.booking_extras import status_badge
from organizations.models import Organization, Teacher
from django.contrib.auth import get_user_model

User = get_user_model()


class Sprint10TestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="t10@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="Sprint 10 School",
            slug="sprint10",
            contact_email="t10@test.com",
            timezone="Europe/Moscow",
            slot_duration_minutes=60,
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Teacher",
        )
        AvailabilityRule.objects.create(
            teacher=self.teacher,
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

    def _next_monday_slot(self):
        tz = ZoneInfo("Europe/Moscow")
        today = timezone.now().astimezone(tz).date()
        days_ahead = (0 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_ahead)
        slots = get_available_slots(self.teacher, monday)
        self.assertTrue(slots)
        return slots[0]

    def test_student_dedup_same_parent_and_child(self):
        slot = self._next_monday_slot()
        data = PublicBookingData(
            parent_name="Мария",
            parent_email="parent@example.com",
            parent_phone="+79990001122",
            child_name="Аня",
            child_age=8,
            notes="",
        )
        create_public_booking(self.org, self.teacher, slot, data)
        self.assertEqual(Student.objects.count(), 1)

        tz = ZoneInfo("Europe/Moscow")
        monday = slot.starts_at.astimezone(tz).date()
        slots = get_available_slots(self.teacher, monday)
        self.assertGreaterEqual(len(slots), 1)
        second_slot = slots[0]
        if second_slot == slot and len(slots) > 1:
            second_slot = slots[1]

        data2 = PublicBookingData(
            parent_name="Мария И.",
            parent_email="PARENT@example.com",
            parent_phone="+79990003344",
            child_name="аня",
            child_age=9,
            notes="повтор",
        )
        create_public_booking(self.org, self.teacher, second_slot, data2)
        self.assertEqual(Student.objects.count(), 1)
        student = Student.objects.get()
        self.assertEqual(student.parent_name, "Мария И.")
        self.assertEqual(student.parent_phone, "+79990003344")
        self.assertEqual(student.child_age, 9)
        self.assertEqual(Booking.objects.count(), 2)

    def test_student_dedup_resets_rejected_status(self):
        slot = self._next_monday_slot()
        data = PublicBookingData(
            parent_name="Иван",
            parent_email="ivan@test.com",
            parent_phone="+7",
            child_name="Петя",
            child_age=10,
            notes="",
        )
        booking = create_public_booking(self.org, self.teacher, slot, data)
        student = booking.student
        student.status = Student.Status.REJECTED
        student.save()

        tz = ZoneInfo("Europe/Moscow")
        monday = slot.starts_at.astimezone(tz).date()
        slots = get_available_slots(self.teacher, monday)
        next_slot = slots[0] if slots[0] != slot else slots[1]
        create_public_booking(self.org, self.teacher, next_slot, data)
        student.refresh_from_db()
        self.assertEqual(student.status, Student.Status.NEW)
        self.assertEqual(Student.objects.count(), 1)

    def test_status_badge_filter(self):
        self.assertEqual(status_badge("pending"), "status-pill--amber")
        self.assertEqual(status_badge("active"), "status-pill--green")
        self.assertEqual(status_badge("unknown"), "status-pill--muted")

    def test_logo_webp_files_exist(self):
        from pathlib import Path

        img = Path(__file__).resolve().parent.parent / "backend" / "static" / "img"
        self.assertTrue((img / "urok-logo-horizontal.webp").exists())
        self.assertTrue((img / "urok-logo-icon.webp").exists())
        stacked = img / "urok-logo-stacked.png"
        self.assertFalse(stacked.exists())
