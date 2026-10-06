"""Booking-related models."""

from django.db import models

from organizations.models import Organization, Teacher


class Student(models.Model):
    """Lead or enrolled student."""

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        TRIAL = "trial", "Пробный"
        ACTIVE = "active", "Учится"
        REJECTED = "rejected", "Отказ"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="Организация",
    )
    parent_name = models.CharField("Имя родителя", max_length=200)
    parent_email = models.EmailField("Email родителя")
    parent_phone = models.CharField("Телефон", max_length=30)
    child_name = models.CharField("Имя ребёнка", max_length=200)
    child_age = models.PositiveSmallIntegerField("Возраст ребёнка")
    notes = models.TextField("Комментарий", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.child_name} ({self.parent_name})"


class AvailabilityRule(models.Model):
    """Weekly availability template for a teacher."""

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="availability_rules",
        verbose_name="Преподаватель",
    )
    weekday = models.PositiveSmallIntegerField(
        "День недели (0=пн)",
        help_text="0 — понедельник, 6 — воскресенье",
    )
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Конец")

    class Meta:
        verbose_name = "Правило доступности"
        verbose_name_plural = "Правила доступности"
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        day = days[self.weekday] if 0 <= self.weekday <= 6 else str(self.weekday)
        return f"{day} {self.start_time:%H:%M}–{self.end_time:%H:%M}"


class Booking(models.Model):
    """Lesson booking."""

    class Type(models.TextChoices):
        TRIAL = "trial", "Пробный"
        REGULAR = "regular", "Регулярный"

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        CONFIRMED = "confirmed", "Подтверждён"
        CANCELLED = "cancelled", "Отменён"
        COMPLETED = "completed", "Завершён"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Организация",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Преподаватель",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Ученик",
    )
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Конец")
    type = models.CharField(
        "Тип",
        max_length=20,
        choices=Type.choices,
        default=Type.TRIAL,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    meeting_url = models.URLField("Ссылка на занятие", blank=True)
    reminder_sent_at = models.DateTimeField("Напоминание отправлено", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "starts_at"],
                name="unique_teacher_starts_at",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student.child_name} — {self.starts_at:%d.%m.%Y %H:%M}"


class BlockedSlot(models.Model):
    """Exception blocking a time range."""

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="blocked_slots",
        verbose_name="Преподаватель",
    )
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Конец")
    reason = models.CharField("Причина", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заблокированный слот"
        verbose_name_plural = "Заблокированные слоты"
        ordering = ["starts_at"]

    def __str__(self) -> str:
        return f"Блок {self.starts_at:%d.%m %H:%M}"
