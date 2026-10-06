"""Email notifications for bookings."""

from django.conf import settings
from django.core.mail import send_mail

from bookings.models import Booking
from bookings.services.slots import get_org_tz


def _format_booking_time(booking: Booking) -> str:
    tz = get_org_tz(booking.organization)
    local_start = booking.starts_at.astimezone(tz)
    return local_start.strftime("%d.%m.%Y в %H:%M")


def send_booking_emails(booking: Booking) -> None:
    """Notify parent and teacher about a new booking."""
    org = booking.organization
    student = booking.student
    when = _format_booking_time(booking)
    tz_label = org.timezone

    parent_subject = f"Запись на урок — {org.name}"
    parent_body = (
        f"Здравствуйте, {student.parent_name}!\n\n"
        f"Вы записали {student.child_name} на пробный урок в «{org.name}».\n"
        f"Дата и время: {when} ({tz_label})\n\n"
        f"Мы свяжемся с вами для подтверждения.\n"
        f"Контакт школы: {org.contact_email}\n"
    )
    send_mail(
        parent_subject,
        parent_body,
        settings.DEFAULT_FROM_EMAIL,
        [student.parent_email],
        fail_silently=False,
    )

    teacher = booking.teacher
    teacher_email = teacher.user.email
    teacher_subject = f"Новая заявка — {student.child_name}"
    teacher_body = (
        f"Новая заявка на пробный урок.\n\n"
        f"Ученик: {student.child_name}, {student.child_age} лет\n"
        f"Родитель: {student.parent_name}\n"
        f"Email: {student.parent_email}\n"
        f"Телефон: {student.parent_phone}\n"
        f"Время: {when} ({tz_label})\n"
    )
    if student.notes:
        teacher_body += f"\nКомментарий: {student.notes}\n"

    send_mail(
        teacher_subject,
        teacher_body,
        settings.DEFAULT_FROM_EMAIL,
        [teacher_email],
        fail_silently=False,
    )


def send_lesson_reminder_emails(booking: Booking) -> None:
    """Send 24h reminder to parent and teacher."""
    org = booking.organization
    student = booking.student
    when = _format_booking_time(booking)
    tz_label = org.timezone

    parent_subject = f"Напоминание: урок завтра — {org.name}"
    parent_body = (
        f"Здравствуйте, {student.parent_name}!\n\n"
        f"Напоминаем: завтра у {student.child_name} урок в «{org.name}».\n"
        f"Дата и время: {when} ({tz_label})\n"
    )
    if booking.meeting_url:
        parent_body += f"\nСсылка на занятие: {booking.meeting_url}\n"
    parent_body += f"\nКонтакт школы: {org.contact_email}\n"

    send_mail(
        parent_subject,
        parent_body,
        settings.DEFAULT_FROM_EMAIL,
        [student.parent_email],
        fail_silently=False,
    )

    teacher = booking.teacher
    teacher_subject = f"Напоминание: урок завтра — {student.child_name}"
    teacher_body = (
        f"Завтра урок с {student.child_name}.\n"
        f"Время: {when} ({tz_label})\n"
        f"Родитель: {student.parent_name}, {student.parent_phone}\n"
    )
    if booking.meeting_url:
        teacher_body += f"Ссылка: {booking.meeting_url}\n"

    send_mail(
        teacher_subject,
        teacher_body,
        settings.DEFAULT_FROM_EMAIL,
        [org.contact_email],
        fail_silently=False,
    )
