"""Public booking page views."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from bookings.decorators import rate_limit_public, record_public_booking
from bookings.forms import DatePickerForm, PublicBookingForm
from bookings.services.booking import (
    PublicBookingData,
    SlotCollisionError,
    SlotUnavailableError,
    create_public_booking,
)
from bookings.services.slots import format_slot_local, get_available_slots, get_org_tz
from organizations.models import Organization


def _get_teacher(org: Organization):
    """Return primary active teacher for organization (v1: single teacher)."""
    return org.teachers.filter(is_active=True).first()


class PublicBookView(View):
    """Public booking flow: pick date, slot, submit form."""

    template_name = "public/book.html"
    slots_partial = "public/partials/slots.html"

    @method_decorator(rate_limit_public)
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        org = get_object_or_404(Organization, slug=slug)
        if not org.accepts_public_bookings():
            return render(request, "public/unavailable.html", {
                "organization": org,
                "subscription_expired": True,
            }, status=403)
        teacher = _get_teacher(org)
        if not teacher:
            return render(request, "public/unavailable.html", {"organization": org}, status=404)

        tz = get_org_tz(org)
        today = timezone.now().astimezone(tz).date()
        date_form = DatePickerForm(initial={"date": today}, tz_name=org.timezone)
        selected_date = today

        if request.GET.get("date"):
            date_form = DatePickerForm({"date": request.GET["date"]}, tz_name=org.timezone)
            if date_form.is_valid():
                selected_date = date_form.cleaned_data["date"]

        slots = get_available_slots(teacher, selected_date)
        slot_labels = [(s, format_slot_local(s, org)) for s in slots]

        # HTMX partial for slots only
        if request.headers.get("HX-Request") and request.GET.get("date"):
            return render(request, self.slots_partial, {
                "slots": slot_labels,
                "organization": org,
                "selected_date": selected_date,
            })

        return render(request, self.template_name, {
            "organization": org,
            "teacher": teacher,
            "date_form": date_form,
            "selected_date": selected_date,
            "today": today,
            "slots": slot_labels,
            "form": PublicBookingForm(),
        })

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        org = get_object_or_404(Organization, slug=slug)
        if not org.accepts_public_bookings():
            return render(request, "public/unavailable.html", {
                "organization": org,
                "subscription_expired": True,
            }, status=403)
        teacher = _get_teacher(org)
        if not teacher:
            return render(request, "public/unavailable.html", {"organization": org}, status=404)

        form = PublicBookingForm(request.POST)
        if not form.is_valid():
            tz = get_org_tz(org)
            today = timezone.now().astimezone(tz).date()
            slots = get_available_slots(teacher, today)
            slot_labels = [(s, format_slot_local(s, org)) for s in slots]
            return render(request, self.template_name, {
                "organization": org,
                "teacher": teacher,
                "date_form": DatePickerForm(initial={"date": today}, tz_name=org.timezone),
                "selected_date": today,
                "today": today,
                "slots": slot_labels,
                "form": form,
            }, status=400)

        data = PublicBookingData(
            parent_name=form.cleaned_data["parent_name"],
            parent_email=form.cleaned_data["parent_email"],
            parent_phone=form.cleaned_data["parent_phone"],
            child_name=form.cleaned_data["child_name"],
            child_age=form.cleaned_data["child_age"],
            notes=form.cleaned_data.get("notes", ""),
        )
        slot = form.get_slot(org, teacher)

        try:
            booking = create_public_booking(org, teacher, slot, data)
        except SlotCollisionError:
            form.add_error(None, "Этот слот только что заняли. Выберите другое время.")
        except SlotUnavailableError as exc:
            form.add_error(None, str(exc))
        else:
            record_public_booking(request)
            return render(request, "public/success.html", {
                "organization": org,
                "booking": booking,
            })

        tz = get_org_tz(org)
        local_day = slot.starts_at.astimezone(tz).date()
        slots = get_available_slots(teacher, local_day)
        slot_labels = [(s, format_slot_local(s, org)) for s in slots]
        return render(request, self.template_name, {
            "organization": org,
            "teacher": teacher,
            "date_form": DatePickerForm(initial={"date": local_day}, tz_name=org.timezone),
            "selected_date": local_day,
            "today": timezone.now().astimezone(tz).date(),
            "slots": slot_labels,
            "form": form,
        }, status=400)
