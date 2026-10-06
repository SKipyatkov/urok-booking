"""Sprint 4 tests: custom error pages and static assets."""

from django.test import Client, TestCase, override_settings


class CustomErrorPageTests(TestCase):
    def setUp(self):
        self.client = Client(raise_request_exception=False)

    @override_settings(DEBUG=False)
    def test_custom_404_for_missing_organization(self):
        response = self.client.get("/s/no-such-school/book/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Страница не найдена", status_code=404)
        self.assertNotContains(response, "Page not found at", status_code=404)

    @override_settings(DEBUG=False)
    def test_custom_404_for_unknown_path(self):
        response = self.client.get("/this-path-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)

    def test_static_css_linked_in_login(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/static/css/app.css")
        self.assertContains(response, "/static/vendor/pico/pico.min.css")
        self.assertNotContains(response, "cdn.jsdelivr.net")
