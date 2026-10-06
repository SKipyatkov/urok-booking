"""Send lesson reminders 24 hours before confirmed bookings."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking
from bookings.services.email import send_lesson_reminder_emails


class Command(BaseCommand):
    help = "Send email reminders for lessons starting in ~24 hours"

    def handle(self, *args, **options):
        now = timezone.now()
        window_start = now + timedelta(hours=23)
        window_end = now + timedelta(hours=25)

        bookings = Booking.objects.filter(
            status=Booking.Status.CONFIRMED,
            starts_at__gte=window_start,
            starts_at__lt=window_end,
            reminder_sent_at__isnull=True,
        ).select_related("organization", "student", "teacher")

        sent = 0
        for booking in bookings:
            send_lesson_reminder_emails(booking)
            booking.reminder_sent_at = timezone.now()
            booking.save(update_fields=["reminder_sent_at"])
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent}"))
