from django.contrib import admin

from .models import Organization, Teacher


class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "plan", "timezone", "slot_duration_minutes")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TeacherInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "user", "is_active")
    list_filter = ("is_active", "organization")
    search_fields = ("name", "user__email")
