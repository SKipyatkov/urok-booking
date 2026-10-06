"""Organization settings forms."""

import re

from django import forms
from django.core.exceptions import ValidationError

from organizations.models import Organization

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class OrganizationSettingsForm(forms.ModelForm):
    """Edit organization profile and booking settings."""

    slug = forms.SlugField(
        label="Адрес для записи",
        help_text="Латиница, цифры и дефис. Старая ссылка перестанет работать после смены.",
    )

    class Meta:
        model = Organization
        fields = (
            "name",
            "slug",
            "description",
            "contact_email",
            "timezone",
            "slot_duration_minutes",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_slug(self) -> str:
        slug = self.cleaned_data["slug"].lower().strip()
        if not SLUG_PATTERN.match(slug):
            raise ValidationError("Используйте только латиницу, цифры и дефис.")
        qs = Organization.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Этот адрес уже занят.")
        return slug
