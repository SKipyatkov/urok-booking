"""Sprint 8 tests: lesson reminder emails."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from bookings.models import Booking, Student
from organizations.models import Organization, Teacher

User = get_user_model()


class ReminderCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="r8@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="Reminder School",
            slug="reminder-school",
            contact_email="school@test.com",
            trial_ends_at=Organization.default_trial_end(),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Teacher",
        )
        self.student = Student.objects.create(
            organization=self.org,
            parent_name="Parent",
            parent_email="parent@test.com",
            parent_phone="+79990001122",
            child_name="Child",
            child_age=9,
        )

    def _create_confirmed_booking_in_24h(self) -> Booking:
        starts = timezone.now() + timedelta(hours=24)
        return Booking.objects.create(
            organization=self.org,
            teacher=self.teacher,
            student=self.student,
            starts_at=starts,
            ends_at=starts + timedelta(hours=1),
            status=Booking.Status.CONFIRMED,
            meeting_url="https://telemost.example/lesson",
        )

    def test_send_reminders_once(self):
        booking = self._create_confirmed_booking_in_24h()
        call_command("send_lesson_reminders")
        self.assertEqual(len(mail.outbox), 2)
        booking.refresh_from_db()
        self.assertIsNotNone(booking.reminder_sent_at)

    def test_reminders_not_duplicated(self):
        self._create_confirmed_booking_in_24h()
        call_command("send_lesson_reminders")
        mail.outbox.clear()
        call_command("send_lesson_reminders")
        self.assertEqual(len(mail.outbox), 0)
