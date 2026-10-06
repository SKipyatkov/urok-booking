from django.contrib import admin

from .models import AvailabilityRule, BlockedSlot, Booking, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("child_name", "parent_name", "parent_email", "status", "organization")
    list_filter = ("status", "organization")
    search_fields = ("child_name", "parent_name", "parent_email")


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("teacher", "weekday", "start_time", "end_time")
    list_filter = ("teacher", "weekday")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "starts_at", "status", "type")
    list_filter = ("status", "type", "organization")
    search_fields = ("student__child_name", "student__parent_name")


@admin.register(BlockedSlot)
class BlockedSlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "starts_at", "ends_at", "reason")
    list_filter = ("teacher",)
