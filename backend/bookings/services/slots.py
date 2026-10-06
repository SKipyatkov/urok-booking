"""Slot generation from availability rules."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone

from bookings.models import AvailabilityRule, BlockedSlot, Booking
from organizations.models import Organization, Teacher


@dataclass(frozen=True)
class TimeSlot:
    """A bookable time window."""

    starts_at: datetime
    ends_at: datetime

    @property
    def iso_start(self) -> str:
        return self.starts_at.isoformat()


def get_org_tz(org: Organization) -> ZoneInfo:
    """Return organization timezone."""
    return ZoneInfo(org.timezone)


def _local_day_bounds(day: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=tz)
    end = datetime.combine(day, time.max, tzinfo=tz)
    return start, end


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def get_available_slots(
    teacher: Teacher,
    day: date,
    *,
    now: datetime | None = None,
) -> list[TimeSlot]:
    """
    Generate free slots for a teacher on a given local calendar day.

    Slots come from AvailabilityRule minus bookings, blocked slots, and past times.
    All returned datetimes are timezone-aware (UTC).
    """
    org = teacher.organization
    tz = get_org_tz(org)
    duration = timedelta(minutes=org.slot_duration_minutes)
    weekday = day.weekday()

    rules = AvailabilityRule.objects.filter(teacher=teacher, weekday=weekday)
    if not rules.exists():
        return []

    day_start_local, day_end_local = _local_day_bounds(day, tz)
    day_start_utc = day_start_local.astimezone(UTC)
    day_end_utc = day_end_local.astimezone(UTC)

    bookings = Booking.objects.filter(
        teacher=teacher,
        starts_at__lt=day_end_utc,
        ends_at__gt=day_start_utc,
    ).exclude(status=Booking.Status.CANCELLED)

    blocked = BlockedSlot.objects.filter(
        teacher=teacher,
        starts_at__lt=day_end_utc,
        ends_at__gt=day_start_utc,
    )

    if now is None:
        now = timezone.now()

    slots: list[TimeSlot] = []
    for rule in rules:
        current_local = datetime.combine(day, rule.start_time, tzinfo=tz)
        rule_end_local = datetime.combine(day, rule.end_time, tzinfo=tz)
        while current_local + duration <= rule_end_local:
            slot_start = current_local.astimezone(UTC)
            slot_end = (current_local + duration).astimezone(UTC)

            if slot_start <= now:
                current_local += duration
                continue

            occupied = any(
                _overlaps(slot_start, slot_end, b.starts_at, b.ends_at) for b in bookings
            )
            blocked_slot = any(
                _overlaps(slot_start, slot_end, b.starts_at, b.ends_at) for b in blocked
            )
            if not occupied and not blocked_slot:
                slots.append(TimeSlot(starts_at=slot_start, ends_at=slot_end))

            current_local += duration

    return sorted(slots, key=lambda s: s.starts_at)


def format_slot_local(slot: TimeSlot, org: Organization) -> str:
    """Format slot start time in organization timezone."""
    tz = get_org_tz(org)
    local = slot.starts_at.astimezone(tz)
    return local.strftime("%H:%M")
