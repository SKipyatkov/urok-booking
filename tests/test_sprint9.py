"""Sprint 9 tests: subscription and YooKassa webhook."""

import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from organizations.models import Organization, Teacher

User = get_user_model()


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sub@test.com", password="pass12345")
        self.org = Organization.objects.create(
            name="Sub School",
            slug="sub-school",
            contact_email="sub@test.com",
            trial_ends_at=timezone.now() + timedelta(days=5),
        )
        self.teacher = Teacher.objects.create(
            organization=self.org,
            user=self.user,
            name="Teacher",
        )
        self.client = Client()
        self.client.login(email="sub@test.com", password="pass12345")

    def test_active_trial_allows_cabinet(self):
        response = self.client.get(reverse("cabinet:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_expired_trial_redirects_to_billing(self):
        self.org.trial_ends_at = timezone.now() - timedelta(days=1)
        self.org.save(update_fields=["trial_ends_at"])
        response = self.client.get(reverse("cabinet:dashboard"))
        self.assertRedirects(response, reverse("cabinet:billing"))

    def test_expired_subscription_blocks_public_booking(self):
        self.org.trial_ends_at = timezone.now() - timedelta(days=1)
        self.org.save(update_fields=["trial_ends_at"])
        response = Client().get(reverse("public:book", kwargs={"slug": self.org.slug}))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "не принимает заявки", status_code=403)


@override_settings(
    YOOKASSA_SHOP_ID="test-shop",
    YOOKASSA_SECRET_KEY="test-secret",
)
class YooKassaWebhookTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name="Pay School",
            slug="pay-school",
            contact_email="pay@test.com",
            trial_ends_at=timezone.now() - timedelta(days=1),
        )

    @patch("config.views.verify_payment_succeeded")
    @patch("config.views.is_configured", return_value=True)
    def test_webhook_extends_subscription(self, _mock_cfg, mock_verify):
        mock_verify.return_value = {
            "organization_id": str(self.org.pk),
            "payment_id": "pay-123",
        }
        payload = {
            "event": "payment.succeeded",
            "object": {"id": "pay-123"},
        }
        response = Client().post(
            reverse("yookassa_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.org.refresh_from_db()
        self.assertTrue(self.org.has_active_subscription())
        self.assertEqual(self.org.yookassa_payment_id, "pay-123")
        self.assertEqual(self.org.plan, Organization.Plan.SOLO)
