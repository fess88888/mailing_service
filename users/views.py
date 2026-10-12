"""
Представления приложения пользователей.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import User
from .forms import UserRegisterForm, UserProfileForm


class UserLoginView(LoginView):
    """Вход в систему."""

    template_name = "users/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("mailing:home")


class UserRegisterView(CreateView):
    """Регистрация с подтверждением email."""

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:registration_confirm_wait")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()
        self._send_verification_email(user)
        return super().form_valid(form)

    def _send_verification_email(self, user):
        token = user.email_verify_token
        verification_url = self.request.build_absolute_uri(
            reverse("users:verify_email", kwargs={"token": token})
        )
        send_mail(
            subject="Подтверждение регистрации",
            message=f"Для подтверждения регистрации перейдите по ссылке: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class EmailVerifyView(TemplateView):
    """Подтверждение email по токену."""

    template_name = "users/verify_email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = kwargs.get("token")
        try:
            user = User.objects.get(email_verify_token=token)
            user.is_active = True
            user.save()
            login(self.request, user)
            context["success"] = True
        except User.DoesNotExist:
            context["success"] = False
        return context


class RegistrationConfirmWaitView(TemplateView):
    """Страница ожидания подтверждения email."""

    template_name = "users/registration_confirm_wait.html"


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Просмотр и редактирование профиля."""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordResetView(PasswordResetView):
    """Восстановление пароля — отправка письма со ссылкой."""

    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    """Установка нового пароля."""

    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class PasswordResetDoneView(TemplateView):
    """Письмо отправлено."""
    template_name = "users/password_reset_done.html"


class PasswordResetCompleteView(TemplateView):
    """Пароль изменён."""
    template_name = "users/password_reset_complete.html"


# ── Менеджер: список пользователей, блокировка ────────────────

@login_required
def user_list_view(request):
    """Список пользователей сервиса (только для менеджеров)."""
    if not request.user.is_manager:
        messages.error(request, "У вас нет прав для просмотра этой страницы.")
        return redirect("mailing:home")
    users = User.objects.filter(is_superuser=False).order_by("email")
    return render(request, "users/user_list.html", {"users": users})


@login_required
def toggle_user_block(request, pk):
    """Блокировка / разблокировка пользователя (только для менеджеров)."""
    if not request.user.is_manager:
        messages.error(request, "У вас нет прав для этого действия.")
        return redirect("mailing:home")
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, "Нельзя заблокировать суперпользователя.")
        return redirect("users:user_list")
    user.is_active = not user.is_active
    user.save()
    action = "разблокирован" if user.is_active else "заблокирован"
    messages.success(request, f"Пользователь {user.email} {action}.")
    return redirect("users:user_list")
