"""Cabinet URL routes."""

from django.urls import path

from . import views_cabinet
from organizations.views_billing import BillingSuccessView, BillingView

app_name = "cabinet"

urlpatterns = [
    path("", views_cabinet.DashboardView.as_view(), name="dashboard"),
    path("schedule/", views_cabinet.ScheduleView.as_view(), name="schedule"),
    path("blocked/", views_cabinet.BlockedSlotsView.as_view(), name="blocked"),
    path("students/", views_cabinet.StudentsView.as_view(), name="students"),
    path("students/export/", views_cabinet.StudentsExportView.as_view(), name="students_export"),
    path("students/<int:pk>/", views_cabinet.StudentDetailView.as_view(), name="student_detail"),
    path("bookings/", views_cabinet.BookingsView.as_view(), name="bookings"),
    path("bookings/export/", views_cabinet.BookingsExportView.as_view(), name="bookings_export"),
    path("bookings/<int:pk>/", views_cabinet.BookingDetailView.as_view(), name="booking_detail"),
    path("settings/", views_cabinet.SettingsView.as_view(), name="settings"),
    path("billing/", BillingView.as_view(), name="billing"),
    path("billing/success/", BillingSuccessView.as_view(), name="billing_success"),
]
