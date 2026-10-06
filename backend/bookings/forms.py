"""Forms for cabinet and public booking."""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from django import forms
from django.utils import timezone

from bookings.models import AvailabilityRule, Booking, Student
from bookings.services.slots import TimeSlot
from organizations.forms import OrganizationSettingsForm
from organizations.models import Organization, Teacher

__all__ = ["OrganizationSettingsForm"]


class AvailabilityRuleForm(forms.ModelForm):
    """Add or edit a weekly availability rule."""

    WEEKDAY_CHOICES = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

    weekday = forms.ChoiceField(label="День недели", choices=WEEKDAY_CHOICES)

    class Meta:
        model = AvailabilityRule
        fields = ("weekday", "start_time", "end_time")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self) -> dict:
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and start >= end:
            raise forms.ValidationError("Время окончания должно быть позже начала.")
        return cleaned


class BookingStatusForm(forms.ModelForm):
    """Update booking status and meeting URL."""

    class Meta:
        model = Booking
        fields = ("status", "meeting_url")
        widgets = {
            "meeting_url": forms.URLInput(attrs={"placeholder": "https://telemost.yandex.ru/..."}),
        }


class StudentStatusForm(forms.ModelForm):
    """Update student funnel status."""

    class Meta:
        model = Student
        fields = ("status",)


class PublicBookingForm(forms.Form):
    """Parent booking request form."""

    parent_name = forms.CharField(label="Ваше имя", max_length=200)
    parent_email = forms.EmailField(label="Email")
    parent_phone = forms.CharField(label="Телефон", max_length=30)
    child_name = forms.CharField(label="Имя ребёнка", max_length=200)
    child_age = forms.IntegerField(label="Возраст ребёнка", min_value=3, max_value=18)
    notes = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    slot_start = forms.CharField(widget=forms.HiddenInput())

    def clean_slot_start(self) -> datetime:
        raw = self.cleaned_data["slot_start"]
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise forms.ValidationError("Некорректный слот.") from exc
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, UTC)
        return dt

    def get_slot(self, org: Organization, teacher: Teacher) -> TimeSlot:
        """Build TimeSlot from cleaned data."""
        starts_at = self.cleaned_data["slot_start"]
        duration_minutes = org.slot_duration_minutes
        from datetime import timedelta

        ends_at = starts_at + timedelta(minutes=duration_minutes)
        return TimeSlot(starts_at=starts_at, ends_at=ends_at)


class DatePickerForm(forms.Form):
    """Select date for slot listing."""

    date = forms.DateField(
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=date.today,
    )

    def __init__(self, *args, tz_name: str = "UTC", **kwargs):
        self.tz_name = tz_name
        super().__init__(*args, **kwargs)

    def clean_date(self) -> date:
        selected = self.cleaned_data["date"]
        tz = ZoneInfo(self.tz_name)
        today = timezone.now().astimezone(tz).date()
        if selected < today:
            raise forms.ValidationError("Нельзя выбрать прошедшую дату.")
        return selected


class BlockedSlotForm(forms.Form):
    """Block a specific date and time range in organization timezone."""

    date = forms.DateField(
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    start_time = forms.TimeField(
        label="Начало",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    end_time = forms.TimeField(
        label="Конец",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    reason = forms.CharField(
        label="Причина",
        required=False,
        max_length=200,
    )

    def clean(self) -> dict:
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and start >= end:
            raise forms.ValidationError("Время окончания должно быть позже начала.")
        return cleaned

    def to_utc_range(self, tz_name: str) -> tuple[datetime, datetime]:
        """Convert local date/time fields to UTC datetimes."""
        tz = ZoneInfo(tz_name)
        day = self.cleaned_data["date"]
        start_local = datetime.combine(day, self.cleaned_data["start_time"], tzinfo=tz)
        end_local = datetime.combine(day, self.cleaned_data["end_time"], tzinfo=tz)
        return start_local.astimezone(UTC), end_local.astimezone(UTC)
