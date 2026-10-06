"""Registration and authentication forms."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.text import slugify

from organizations.models import Organization, Teacher

User = get_user_model()


class RegisterForm(forms.Form):
    """Teacher registration: creates User + Organization + Teacher."""

    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)
    organization_name = forms.CharField(label="Название школы / репетитора", max_length=200)
    teacher_name = forms.CharField(label="Ваше имя", max_length=200)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self) -> dict:
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned

    def save(self) -> User:
        """Create user, organization and teacher profile."""
        email = self.cleaned_data["email"]
        org_name = self.cleaned_data["organization_name"]
        base_slug = slugify(org_name, allow_unicode=True) or "school"
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        user = User.objects.create_user(
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["teacher_name"],
        )
        org = Organization.objects.create(
            name=org_name,
            slug=slug,
            contact_email=email,
            trial_ends_at=Organization.default_trial_end(),
        )
        Teacher.objects.create(
            organization=org,
            user=user,
            name=self.cleaned_data["teacher_name"],
        )
        return user


class EmailAuthenticationForm(AuthenticationForm):
    """Login form with email field label."""

    username = forms.EmailField(label="Email")
