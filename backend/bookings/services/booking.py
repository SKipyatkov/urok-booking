"""Booking creation with collision protection."""

from dataclasses import dataclass

from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking, Student
from bookings.services.email import send_booking_emails
from bookings.services.slots import TimeSlot, get_available_slots
from organizations.models import Organization, Teacher


class SlotUnavailableError(Exception):
    """Raised when the requested slot cannot be booked."""


class SlotCollisionError(SlotUnavailableError):
    """Raised when another booking already occupies the slot."""


@dataclass
class PublicBookingData:
    """Data from public booking form."""

    parent_name: str
    parent_email: str
    parent_phone: str
    child_name: str
    child_age: int
    notes: str


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_child_key(name: str) -> str:
    return name.strip().casefold()


def _get_or_create_student(
    organization: Organization, data: PublicBookingData
) -> Student:
    """Reuse student when parent email and child name match."""
    email = _normalize_email(data.parent_email)
    child = data.child_name.strip()
    child_key = _normalize_child_key(child)
    for student in Student.objects.filter(
        organization=organization,
        parent_email__iexact=email,
    ):
        if _normalize_child_key(student.child_name) == child_key:
            student.parent_name = data.parent_name.strip()
            student.parent_phone = data.parent_phone.strip()
            student.child_age = data.child_age
            if data.notes:
                student.notes = data.notes
            if student.status == Student.Status.REJECTED:
                student.status = Student.Status.NEW
            student.save()
            return student
    return Student.objects.create(
        organization=organization,
        parent_name=data.parent_name.strip(),
        parent_email=email,
        parent_phone=data.parent_phone.strip(),
        child_name=child,
        child_age=data.child_age,
        notes=data.notes,
        status=Student.Status.NEW,
    )


def _slot_is_free(teacher: Teacher, slot: TimeSlot) -> bool:
    """Check slot is still available (service-level guard)."""
    overlapping = Booking.objects.filter(
        teacher=teacher,
        starts_at__lt=slot.ends_at,
        ends_at__gt=slot.starts_at,
    ).exclude(status=Booking.Status.CANCELLED)
    return not overlapping.exists()


def create_public_booking(
    organization: Organization,
    teacher: Teacher,
    slot: TimeSlot,
    data: PublicBookingData,
) -> Booking:
    """
    Create student and pending trial booking for a public request.

    Raises SlotUnavailableError if slot is not bookable.
    """
    if slot.starts_at <= timezone.now():
        raise SlotUnavailableError("Нельзя записаться на прошедшее время.")

    if not _slot_is_free(teacher, slot):
        raise SlotCollisionError("Этот слот уже занят.")

    local_day = slot.starts_at.astimezone(
        ZoneInfo(organization.timezone)
    ).date()
    available = get_available_slots(teacher, local_day)
    if slot not in available:
        raise SlotUnavailableError("Выбранный слот недоступен.")

    try:
        with transaction.atomic():
            student = _get_or_create_student(organization, data)
            booking = Booking.objects.create(
                organization=organization,
                teacher=teacher,
                student=student,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                type=Booking.Type.TRIAL,
                status=Booking.Status.PENDING,
            )
    except IntegrityError as exc:
        raise SlotCollisionError("Этот слот уже занят.") from exc

    send_booking_emails(booking)
    return booking
