"""Cabinet access mixin."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect

from organizations.models import Teacher


class TeacherRequiredMixin(LoginRequiredMixin):
    """Ensure user has an active teacher profile."""

    subscription_exempt = False

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, "teacher_profile"):
            return redirect("accounts:register")
        self.teacher = request.user.teacher_profile
        self.organization = self.teacher.organization
        if (
            not self.subscription_exempt
            and not self.organization.has_active_subscription()
        ):
            return redirect("cabinet:billing")
        return super().dispatch(request, *args, **kwargs)
