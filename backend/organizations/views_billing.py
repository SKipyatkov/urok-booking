"""Billing and subscription views."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from bookings.mixins import TeacherRequiredMixin
from organizations.services.yookassa import (
    PaymentNotConfiguredError,
    create_subscription_payment,
    is_configured,
)


class BillingView(TeacherRequiredMixin, View):
    """Subscription status and payment."""

    subscription_exempt = True
    template_name = "cabinet/billing.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        org = self.organization
        return render(request, self.template_name, {
            "organization": org,
            "price": settings.SUBSCRIPTION_SOLO_PRICE_RUB,
            "yookassa_configured": is_configured(),
            "is_active": org.has_active_subscription(),
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        org = self.organization
        return_url = request.build_absolute_uri(reverse("cabinet:billing_success"))
        try:
            payment = create_subscription_payment(org, return_url)
        except PaymentNotConfiguredError:
            messages.error(
                request,
                "Оплата временно недоступна. Настройте ЮKassa или свяжитесь с поддержкой.",
            )
            return redirect("cabinet:billing")
        return redirect(payment["confirmation_url"])


class BillingSuccessView(TeacherRequiredMixin, View):
    """Return page after YooKassa redirect."""

    subscription_exempt = True
    template_name = "cabinet/billing_success.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {
            "organization": self.organization,
            "is_active": self.organization.has_active_subscription(),
        })
