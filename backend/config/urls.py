"""URL configuration for Urok Booking."""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from config import views


def home(request):
    if request.user.is_authenticated:
        return redirect("cabinet:dashboard")
    return views.landing(request)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health_check, name="health"),
    path("", home, name="home"),
    path("", include("accounts.urls")),
    path("cabinet/", include("bookings.urls_cabinet")),
    path("s/", include("bookings.urls_public")),
    path("webhooks/yookassa/", views.yookassa_webhook, name="yookassa_webhook"),
]

handler404 = "config.views.page_not_found"
handler500 = "config.views.server_error"
