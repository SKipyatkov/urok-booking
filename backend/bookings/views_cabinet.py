"""Teacher cabinet views."""

import csv
from datetime import timedelta

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView

from bookings.forms import (
    AvailabilityRuleForm,
    BlockedSlotForm,
    BookingStatusForm,
    OrganizationSettingsForm,
    StudentStatusForm,
)
from bookings.mixins import TeacherRequiredMixin
from bookings.models import AvailabilityRule, BlockedSlot, Booking, Student
from bookings.services.slots import get_org_tz


class DashboardView(TeacherRequiredMixin, TemplateView):
    """Main cabinet dashboard with week calendar."""

    template_name = "cabinet/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        org = self.organization
        teacher = self.teacher
        tz = get_org_tz(org)
        now = timezone.now()
        today = now.astimezone(tz).date()
        week_start = today - timedelta(days=today.weekday())
        try:
            week_offset = int(self.request.GET.get("week", 0))
        except (TypeError, ValueError):
            week_offset = 0
        week_start = week_start + timedelta(weeks=week_offset)

        days = []
        all_bookings = list(
            Booking.objects.filter(teacher=teacher)
            .exclude(status=Booking.Status.CANCELLED)
            .select_related("student")
        )
        for i in range(7):
            day = week_start + timedelta(days=i)
            local_bookings = [
                b for b in all_bookings if b.starts_at.astimezone(tz).date() == day
            ]
            days.append({"date": day, "bookings": local_bookings})

        ctx.update({
            "organization": org,
            "teacher": teacher,
            "days": days,
            "today": today,
            "week_offset": week_offset,
            "prev_week": week_offset - 1,
            "next_week": week_offset + 1,
            "public_url": self.request.build_absolute_uri(
                reverse("public:book", kwargs={"slug": org.slug})
            ),
            "pending_count": Booking.objects.filter(
                teacher=teacher, status=Booking.Status.PENDING
            ).count(),
            "stats": {
                "new_students": Student.objects.filter(
                    organization=org, status=Student.Status.NEW
                ).count(),
                "pending_bookings": Booking.objects.filter(
                    organization=org, status=Booking.Status.PENDING
                ).count(),
                "trial_students": Student.objects.filter(
                    organization=org, status=Student.Status.TRIAL
                ).count(),
                "active_students": Student.objects.filter(
                    organization=org, status=Student.Status.ACTIVE
                ).count(),
            },
        })
        return ctx


class ScheduleView(TeacherRequiredMixin, View):
    """Manage weekly availability rules."""

    template_name = "cabinet/schedule.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        rules = AvailabilityRule.objects.filter(teacher=self.teacher)
        return render(request, self.template_name, {
            "rules": rules,
            "form": AvailabilityRuleForm(),
            "organization": self.organization,
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        if "delete_rule" in request.POST:
            rule = get_object_or_404(
                AvailabilityRule, pk=request.POST["delete_rule"], teacher=self.teacher
            )
            rule.delete()
            messages.success(request, "Правило удалено.")
            return redirect("cabinet:schedule")

        form = AvailabilityRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.teacher = self.teacher
            rule.weekday = int(form.cleaned_data["weekday"])
            rule.save()
            messages.success(request, "Расписание обновлено.")
            return redirect("cabinet:schedule")

        rules = AvailabilityRule.objects.filter(teacher=self.teacher)
        return render(request, self.template_name, {
            "rules": rules,
            "form": form,
            "organization": self.organization,
        })


class StudentsView(TeacherRequiredMixin, ListView):
    """List students with status filter."""

    template_name = "cabinet/students.html"
    context_object_name = "students"
    paginate_by = 20

    def get_queryset(self):
        qs = Student.objects.filter(organization=self.organization)
        status = self.request.GET.get("status")
        if status and status in dict(Student.Status.choices):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        ctx["status_filter"] = self.request.GET.get("status", "")
        ctx["status_choices"] = Student.Status.choices
        return ctx


class StudentDetailView(TeacherRequiredMixin, View):
    """View and update student status."""

    template_name = "cabinet/student_detail.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        student = get_object_or_404(Student, pk=pk, organization=self.organization)
        bookings = student.bookings.select_related("teacher").order_by("-starts_at")
        return render(request, self.template_name, {
            "student": student,
            "bookings": bookings,
            "form": StudentStatusForm(instance=student),
            "organization": self.organization,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        student = get_object_or_404(Student, pk=pk, organization=self.organization)
        form = StudentStatusForm(request.POST, instance=student)
        bookings = student.bookings.select_related("teacher").order_by("-starts_at")
        if form.is_valid():
            form.save()
            messages.success(request, "Статус ученика обновлён.")
            return redirect("cabinet:student_detail", pk=pk)
        return render(request, self.template_name, {
            "student": student,
            "bookings": bookings,
            "form": form,
            "organization": self.organization,
        })


class BookingsView(TeacherRequiredMixin, ListView):
    """List all bookings."""

    template_name = "cabinet/bookings.html"
    context_object_name = "bookings"
    paginate_by = 20

    def get_queryset(self):
        qs = Booking.objects.filter(
            organization=self.organization
        ).select_related("student", "teacher")
        status = self.request.GET.get("status")
        if status and status in dict(Booking.Status.choices):
            qs = qs.filter(status=status)
        return qs.order_by("-starts_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        ctx["status_filter"] = self.request.GET.get("status", "")
        ctx["status_choices"] = Booking.Status.choices
        return ctx


class BookingDetailView(TeacherRequiredMixin, View):
    """View and update booking."""

    template_name = "cabinet/booking_detail.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = get_object_or_404(
            Booking, pk=pk, organization=self.organization
        )
        return render(request, self.template_name, {
            "booking": booking,
            "form": BookingStatusForm(instance=booking),
            "organization": self.organization,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = get_object_or_404(
            Booking, pk=pk, organization=self.organization
        )
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Бронирование обновлено.")
            return redirect("cabinet:booking_detail", pk=pk)
        return render(request, self.template_name, {
            "booking": booking,
            "form": form,
            "organization": self.organization,
        })


class SettingsView(TeacherRequiredMixin, View):
    """Organization settings."""

    template_name = "cabinet/settings.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {
            "form": OrganizationSettingsForm(instance=self.organization),
            "organization": self.organization,
            "public_url": request.build_absolute_uri(
                reverse("public:book", kwargs={"slug": self.organization.slug})
            ),
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        old_slug = self.organization.slug
        form = OrganizationSettingsForm(request.POST, instance=self.organization)
        if form.is_valid():
            form.save()
            if form.cleaned_data["slug"] != old_slug:
                messages.warning(
                    request,
                    "Адрес изменён. Старая ссылка для записи больше не работает.",
                )
            else:
                messages.success(request, "Настройки сохранены.")
            return redirect("cabinet:settings")
        return render(request, self.template_name, {
            "form": form,
            "organization": self.organization,
            "public_url": request.build_absolute_uri(
                reverse("public:book", kwargs={"slug": self.organization.slug})
            ),
        })


class BlockedSlotsView(TeacherRequiredMixin, View):
    """Manage one-off blocked time ranges."""

    template_name = "cabinet/blocked.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        blocked = BlockedSlot.objects.filter(teacher=self.teacher)
        return render(request, self.template_name, {
            "blocked_slots": blocked,
            "form": BlockedSlotForm(),
            "organization": self.organization,
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        if "delete_blocked" in request.POST:
            slot = get_object_or_404(
                BlockedSlot,
                pk=request.POST["delete_blocked"],
                teacher=self.teacher,
            )
            slot.delete()
            messages.success(request, "Блокировка удалена.")
            return redirect("cabinet:blocked")

        form = BlockedSlotForm(request.POST)
        if form.is_valid():
            starts_at, ends_at = form.to_utc_range(self.organization.timezone)
            BlockedSlot.objects.create(
                teacher=self.teacher,
                starts_at=starts_at,
                ends_at=ends_at,
                reason=form.cleaned_data.get("reason", ""),
            )
            messages.success(request, "Время заблокировано.")
            return redirect("cabinet:blocked")

        blocked = BlockedSlot.objects.filter(teacher=self.teacher)
        return render(request, self.template_name, {
            "blocked_slots": blocked,
            "form": form,
            "organization": self.organization,
        })


class StudentsExportView(TeacherRequiredMixin, View):
    """Export students as CSV."""

    def get(self, request: HttpRequest) -> HttpResponse:
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="students.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow([
            "Ребёнок", "Возраст", "Родитель", "Email", "Телефон", "Статус", "Дата",
        ])
        for student in Student.objects.filter(organization=self.organization).order_by("-created_at"):
            writer.writerow([
                student.child_name,
                student.child_age,
                student.parent_name,
                student.parent_email,
                student.parent_phone,
                student.get_status_display(),
                student.created_at.strftime("%d.%m.%Y"),
            ])
        return response


class BookingsExportView(TeacherRequiredMixin, View):
    """Export bookings as CSV."""

    def get(self, request: HttpRequest) -> HttpResponse:
        org = self.organization
        tz = get_org_tz(org)
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="bookings.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow([
            "Дата", "Ученик", "Родитель", "Статус", "Тип", "Ссылка на занятие",
        ])
        bookings = Booking.objects.filter(organization=org).select_related("student").order_by("-starts_at")
        for booking in bookings:
            local_start = booking.starts_at.astimezone(tz).strftime("%d.%m.%Y %H:%M")
            writer.writerow([
                local_start,
                booking.student.child_name,
                booking.student.parent_name,
                booking.get_status_display(),
                booking.get_type_display(),
                booking.meeting_url,
            ])
        return response
