"""Template tags for timezone display and UI helpers."""

from django import template
from django.urls import Resolver404, resolve

from bookings.services.slots import get_org_tz

register = template.Library()

_STATUS_BADGE = {
    "new": "status-pill--blue",
    "trial": "status-pill--amber",
    "active": "status-pill--green",
    "rejected": "status-pill--red",
    "pending": "status-pill--amber",
    "confirmed": "status-pill--green",
    "cancelled": "status-pill--muted",
    "completed": "status-pill--blue",
}


@register.filter
def local_datetime(dt, organization):
    """Format UTC datetime in organization timezone."""
    if dt is None:
        return ""
    tz = get_org_tz(organization)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


@register.filter
def status_badge(status):
    """CSS class for status pill."""
    return _STATUS_BADGE.get(status, "status-pill--muted")


@register.simple_tag(takes_context=True)
def nav_active(context, *url_names):
    """Return active class when current cabinet view matches."""
    request = context.get("request")
    if not request:
        return ""
    try:
        match = resolve(request.path)
    except Resolver404:
        return ""
    view_name = match.view_name or ""
    for name in url_names:
        if view_name == f"cabinet:{name}":
            return "nav-link--active"
    return ""
