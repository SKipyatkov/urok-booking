from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
