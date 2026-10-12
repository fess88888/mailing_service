"""
Представления приложения рассылок.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone

from .models import Recipient, Message, Mailing, Attempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing, get_home_stats


# ── Mixin для фильтрации по владельцу ─────────────────────────

class OwnerQuerySetMixin:
    """Фильтрует queryset по владельцу; для менеджеров — все записи."""

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)


class OwnerCreateMixin:
    """Присваивает owner при создании."""

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# ── Главная страница (с кешированием) ─────────────────────────

class HomeView(TemplateView):
    """Главная страница со статистикой. Кешируется на 60 секунд."""

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Берём данные из кэша
        cache_key = "home_stats"
        stats = cache.get(cache_key)
        if stats is None:
            stats = get_home_stats()
            cache.set(cache_key, stats, 60)  # 60 секунд
        context["stats"] = stats
        return context


# ── Получатели (Recipients) ────────────────────────────────────

class RecipientListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientDetailView(LoginRequiredMixin, OwnerQuerySetMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, OwnerCreateMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        messages.success(self.request, "Получатель добавлен.")
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Получатель обновлён.")
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# ── Сообщения (Messages) ───────────────────────────────────────

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Сообщение создано.")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение обновлено.")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# ── Рассылки (Mailings) ────────────────────────────────────────

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        qs = super().get_queryset().select_related("message", "owner")
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all()[:20]
        context["now"] = timezone.now()
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Рассылка создана.")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Рассылка обновлена.")
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# ── Ручная отправка рассылки ────────────────────────────────────

from django.contrib.auth.decorators import login_required

@login_required
def send_mailing_view(request, pk):
    """Запускает рассылку вручную."""
    mailing = get_object_or_404(Mailing, pk=pk)
    # Проверка прав
    if not request.user.is_manager and mailing.owner != request.user:
        messages.error(request, "У вас нет прав для этой рассылки.")
        return redirect("mailing:mailing_list")

    try:
        success_count, fail_count = send_mailing(mailing)
        messages.success(
            request,
            f"Рассылка отправлена: успешно — {success_count}, с ошибками — {fail_count}."
        )
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Произошла ошибка: {e}")

    return redirect("mailing:mailing_detail", pk=pk)


# ── Менеджер: отключение рассылки ──────────────────────────────

@login_required
def toggle_mailing_disable(request, pk):
    """Отключение/включение рассылки менеджером."""
    if not request.user.is_manager:
        messages.error(request, "У вас нет прав для этого действия.")
        return redirect("mailing:mailing_list")
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_disabled = not mailing.is_disabled
    mailing.save()
    action = "включена" if not mailing.is_disabled else "отключена"
    messages.success(request, f"Рассылка #{mailing.pk} {action}.")
    return redirect("mailing:mailing_list")


# ── Статистика (с кешированием) ────────────────────────────────

class StatisticsView(LoginRequiredMixin, TemplateView):
    """Страница статистики по попыткам рассылок."""

    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cache_key = f"stats_{user.pk}"

        stats = cache.get(cache_key)
        if stats is None:
            if user.is_manager:
                mailings = Mailing.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)

            attempts = Attempt.objects.filter(mailing__in=mailings)
            total = attempts.count()
            success = attempts.filter(status=Attempt.STATUS_SUCCESS).count()
            failed = attempts.filter(status=Attempt.STATUS_FAILED).count()
            sent_messages = total

            stats = {
                "total_attempts": total,
                "success_count": success,
                "fail_count": failed,
                "sent_messages": sent_messages,
                "mailings_count": mailings.count(),
            }
            cache.set(cache_key, stats, 60)

        context["stats"] = stats
        return context


# ── Попытки (Attempts) ────────────────────────────────────────

class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("mailing", "mailing__owner")
        if self.request.user.is_manager:
            return qs
        return qs.filter(mailing__owner=self.request.user)
