"""Account views: login, logout, register, password reset/change, profile."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import (
    ProfileForm, RegisterForm, StyledAuthenticationForm, StyledPasswordChangeForm,
    StyledPasswordResetForm, StyledSetPasswordForm,
)


class SiteLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class SiteLogoutView(auth_views.LogoutView):
    """Logout requires POST (Django 5); the nav bar renders a small form for it."""


class RegisterView(CreateView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy('jscc-dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_open'] = settings.ALLOW_REGISTRATION
        return context

    def post(self, request, *args, **kwargs):
        if not settings.ALLOW_REGISTRATION:
            messages.error(request, "Registration is currently closed.")
            return redirect('login')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome! Your account is ready.")
        return response


class SitePasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    form_class = StyledPasswordResetForm
    success_url = reverse_lazy('password-reset-done')


class SitePasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class SitePasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy('password-reset-complete')


class SitePasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class SitePasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change_form.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy('password-change-done')


class SitePasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)
