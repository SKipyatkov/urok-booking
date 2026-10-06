"""Create demo teacher and sample schedule for QA."""

from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bookings.models import AvailabilityRule
from organizations.models import Organization, Teacher

User = get_user_model()

DEMO_EMAIL = "demo@urok-booking.local"
DEMO_PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Create demo organization, teacher and Mon-Fri 10-18 schedule"

    def handle(self, *args, **options):
        if User.objects.filter(email=DEMO_EMAIL).exists():
            teacher = Teacher.objects.get(user__email=DEMO_EMAIL)
            org = teacher.organization
            self.stdout.write(self.style.WARNING("Demo user already exists."))
        else:
            user = User.objects.create_user(
                email=DEMO_EMAIL,
                password=DEMO_PASSWORD,
                first_name="Анна",
            )
            org = Organization.objects.create(
                name="Демо-школа программирования",
                slug="demo-school",
                description="Пробные уроки Python для детей 8–14 лет",
                contact_email=DEMO_EMAIL,
                trial_ends_at=Organization.default_trial_end(),
            )
            teacher = Teacher.objects.create(
                organization=org,
                user=user,
                name="Анна Демо",
            )
            self.stdout.write(self.style.SUCCESS("Demo user created."))

        for weekday in range(5):
            AvailabilityRule.objects.get_or_create(
                teacher=teacher,
                weekday=weekday,
                defaults={"start_time": time(10, 0), "end_time": time(18, 0)},
            )

        self.stdout.write(f"Email: {DEMO_EMAIL}")
        self.stdout.write(f"Password: {DEMO_PASSWORD}")
        self.stdout.write(f"Public URL slug: {org.slug}")
        self.stdout.write("Run server and open /s/demo-school/book/")
