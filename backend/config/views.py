"""Project-level views."""

import json
import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from organizations.models import Organization
from organizations.services.yookassa import is_configured, verify_payment_succeeded

logger = logging.getLogger(__name__)


def health_check(request):
    """Liveness probe for monitoring and Docker healthcheck."""
    return JsonResponse({"status": "ok"})


def landing(request):
    """Public landing page for guests."""
    return render(request, "landing.html")


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """Handle YooKassa payment notifications."""
    if not is_configured():
        return HttpResponse(status=503)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    event = payload.get("event")
    if event != "payment.succeeded":
        return HttpResponse(status=200)

    payment_obj = payload.get("object", {})
    payment_id = payment_obj.get("id")
    if not payment_id:
        return HttpResponse(status=400)

    verified = verify_payment_succeeded(payment_id)
    if not verified:
        return HttpResponse(status=200)

    org_id = verified.get("organization_id")
    if not org_id:
        logger.warning("YooKassa webhook without organization_id: %s", payment_id)
        return HttpResponse(status=200)

    try:
        org = Organization.objects.get(pk=int(org_id))
    except (Organization.DoesNotExist, ValueError):
        logger.warning("YooKassa webhook unknown org %s", org_id)
        return HttpResponse(status=200)

    org.yookassa_payment_id = payment_id
    org.extend_subscription(days=30, payment_id=payment_id)
    return HttpResponse(status=200)


def page_not_found(request, exception):
    """Custom 404 page (used when DEBUG=False)."""
    return render(request, "404.html", status=404)


def server_error(request):
    """Custom 500 page."""
    return render(request, "500.html", status=500)
