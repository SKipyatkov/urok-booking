"""Organization and teacher models."""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """School or solo tutor profile."""

    class Plan(models.TextChoices):
        FREE_TRIAL = "free_trial", "Пробный"
        SOLO = "solo", "Соло"
        SCHOOL = "school", "Школа"

    class SlotDuration(models.IntegerChoices):
        THIRTY = 30, "30 минут"
        SIXTY = 60, "60 минут"

    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Slug", unique=True, max_length=100)
    description = models.TextField("Описание", blank=True)
    contact_email = models.EmailField("Контактный email")
    timezone = models.CharField("Часовой пояс", max_length=63, default="Europe/Moscow")
    slot_duration_minutes = models.PositiveSmallIntegerField(
        "Длительность слота (мин)",
        choices=SlotDuration.choices,
        default=SlotDuration.SIXTY,
    )
    plan = models.CharField(
        "Тариф",
        max_length=20,
        choices=Plan.choices,
        default=Plan.FREE_TRIAL,
    )
    trial_ends_at = models.DateTimeField("Пробный период до", null=True, blank=True)
    subscription_paid_until = models.DateTimeField("Подписка оплачена до", null=True, blank=True)
    yookassa_payment_id = models.CharField(
        "Последний платёж ЮKassa",
        max_length=64,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self) -> str:
        return self.name

    def has_active_subscription(self) -> bool:
        """Return True if trial or paid subscription is still active."""
        now = timezone.now()
        if self.subscription_paid_until and self.subscription_paid_until > now:
            return True
        if self.trial_ends_at and self.trial_ends_at > now:
            return True
        return False

    def accepts_public_bookings(self) -> bool:
        """Public booking page is available only with active subscription."""
        return self.has_active_subscription()

    def extend_subscription(self, days: int = 30, payment_id: str = "") -> None:
        """Extend paid subscription from now or current end date."""
        now = timezone.now()
        base = self.subscription_paid_until if self.subscription_paid_until and self.subscription_paid_until > now else now
        self.subscription_paid_until = base + timedelta(days=days)
        self.plan = self.Plan.SOLO
        update_fields = ["subscription_paid_until", "plan"]
        if payment_id:
            self.yookassa_payment_id = payment_id
            update_fields.append("yookassa_payment_id")
        self.save(update_fields=update_fields)

    @classmethod
    def default_trial_end(cls):
        return timezone.now() + timedelta(days=settings.TRIAL_DAYS)


class Teacher(models.Model):
    """Teacher linked to organization and user account."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="teachers",
        verbose_name="Организация",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name="Пользователь",
    )
    name = models.CharField("Имя", max_length=200)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self) -> str:
        return self.name
