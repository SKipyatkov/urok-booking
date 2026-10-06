"""YooKassa payment integration."""

from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings

from organizations.models import Organization


class PaymentNotConfiguredError(Exception):
    """Raised when YooKassa credentials are missing."""


def is_configured() -> bool:
    return bool(settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


def _configure() -> None:
    if not is_configured():
        raise PaymentNotConfiguredError("ЮKassa не настроена. Укажите YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.")
    from yookassa import Configuration

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_subscription_payment(org: Organization, return_url: str) -> dict[str, Any]:
    """Create a redirect payment for solo subscription."""
    _configure()
    from yookassa import Payment

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {
                "value": f"{settings.SUBSCRIPTION_SOLO_PRICE_RUB:.2f}",
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "capture": True,
            "description": f"Подписка Urok Booking — {org.name}",
            "metadata": {"organization_id": str(org.pk)},
        },
        idempotence_key,
    )
    org.yookassa_payment_id = payment.id
    org.save(update_fields=["yookassa_payment_id"])
    return {
        "id": payment.id,
        "confirmation_url": payment.confirmation.confirmation_url,
    }


def verify_payment_succeeded(payment_id: str) -> dict[str, Any] | None:
    """Fetch payment from API and return metadata if succeeded."""
    _configure()
    from yookassa import Payment

    payment = Payment.find_one(payment_id)
    if payment.status != "succeeded":
        return None
    return {
        "organization_id": payment.metadata.get("organization_id"),
        "payment_id": payment.id,
    }
