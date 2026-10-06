"""Template context for cabinet pages."""

from bookings.models import Booking


def cabinet_context(request):
    """Pending bookings badge in cabinet navigation."""
    if request.user.is_authenticated and hasattr(request.user, "teacher_profile"):
        teacher = request.user.teacher_profile
        return {
            "pending_count": Booking.objects.filter(
                teacher=teacher,
                status=Booking.Status.PENDING,
            ).count(),
        }
    return {}
