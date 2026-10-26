from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import AdministratorAuthenticationForm, RegistrationForm


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    extra_context = {
        "page_title": "Welcome back",
        "page_description": "Sign in to continue your learning journey.",
        "submit_label": "Sign in",
        "auth_page": "login",
    }


class AdministratorLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AdministratorAuthenticationForm
    redirect_authenticated_user = True
    extra_context = {
        "page_title": "Administrator sign in",
        "page_description": "Sign in with your administrator account to manage the portal.",
        "submit_label": "Sign in as administrator",
        "auth_page": "administrator_login",
    }

    def get_success_url(self):
        return reverse_lazy("core:administrator_dashboard")


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


class RegistrationView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("core:learner_dashboard")
    extra_context = {
        "page_title": "Create your account",
        "page_description": "Join Capacity Connect and start learning.",
        "submit_label": "Create account",
        "auth_page": "register",
    }

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            "Your account is ready. Welcome to Capacity Connect!",
        )
        return super().form_valid(form)


class AccountPasswordChangeView(PasswordChangeView):
    template_name = "accounts/auth_base.html"
    success_url = reverse_lazy("accounts:password_change_done")
    extra_context = {
        "page_title": "Change your password",
        "page_description": "Choose a strong password you have not used elsewhere.",
        "submit_label": "Update password",
    }

    def form_valid(self, form):
        messages.success(self.request, "Your password was changed.")
        return super().form_valid(form)


class AccountPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


class AccountPasswordResetView(PasswordResetView):
    template_name = "accounts/auth_base.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    extra_context = {
        "page_title": "Reset your password",
        "page_description": "Enter your account email and we will send reset instructions.",
        "submit_label": "Send reset link",
    }


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/auth_base.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    extra_context = {
        "page_title": "Choose a new password",
        "page_description": "Enter and confirm your new password.",
        "submit_label": "Save new password",
    }


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"