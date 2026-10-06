"""Rate limiting for public endpoints."""

from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP from request."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_limit_key(request: HttpRequest) -> str:
    return f"public_booking_rate:{get_client_ip(request)}"


def is_rate_limited(request: HttpRequest) -> bool:
    """Return True if IP exceeded the public booking rate limit."""
    limit = getattr(settings, "PUBLIC_BOOKING_RATE_LIMIT", 10)
    return cache.get(_rate_limit_key(request), 0) >= limit


def record_public_booking(request: HttpRequest) -> None:
    """Increment rate limit counter after a successful booking."""
    key = _rate_limit_key(request)
    count = cache.get(key, 0)
    cache.set(key, count + 1, timeout=3600)


def rate_limit_public(view_func):
    """Block POST requests when IP exceeded rate limit (check only, no increment)."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method == "POST" and is_rate_limited(request):
            return render(request, "public/rate_limited.html", status=429)
        return view_func(request, *args, **kwargs)

    return wrapper
