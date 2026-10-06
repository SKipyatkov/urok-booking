"""Sprint 6 tests: healthcheck and prod basics."""

from django.test import Client, TestCase


class HealthCheckTests(TestCase):
    def test_health_returns_ok(self):
        response = Client().get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
