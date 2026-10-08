"""
Формы приложения рассылок.
"""
from django import forms
from django.utils import timezone
from .models import Recipient, Message, Mailing


class RecipientForm(forms.ModelForm):
    """Форма получателя рассылки."""

    class Meta:
        model = Recipient
        fields = ("email", "full_name", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class MessageForm(forms.ModelForm):
    """Форма сообщения."""

    class Meta:
        model = Message
        fields = ("subject", "body")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 6}),
        }


class MailingForm(forms.ModelForm):
    """Форма рассылки с валидацией временных полей."""

    class Meta:
        model = Mailing
        fields = ("start_time", "end_time", "message", "recipients")
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "recipients": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Ограничиваем выбор сообщений и получателей — только свои
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        if start and end:
            if start < timezone.now():
                raise forms.ValidationError({"start_time": "Дата начала не может быть в прошлом."})
            if start >= end:
                raise forms.ValidationError({"end_time": "Дата окончания должна быть позже даты начала."})

        if not cleaned.get("recipients"):
            raise forms.ValidationError({"recipients": "Выберите хотя бы одного получателя."})

        return cleaned
