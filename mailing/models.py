"""
Модели приложения рассылок.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from users.models import User


class Recipient(models.Model):
    """Получатель рассылки (клиент)."""

    email = models.EmailField("Email", unique=True)
    full_name = models.CharField("Ф. И. О.", max_length=200)
    comment = models.TextField("Комментарий", blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="recipients", verbose_name="Владелец",
        null=True, blank=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    """Сообщение для рассылки."""

    subject = models.CharField("Тема письма", max_length=250)
    body = models.TextField("Тело письма")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="messages", verbose_name="Владелец",
        null=True, blank=True,
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Рассылка — связывает сообщение и получателей,
    имеет окно времени для отправки.
    """

    STATUS_CREATED = "Создана"
    STATUS_STARTED = "Запущена"
    STATUS_COMPLETED = "Завершена"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    start_time = models.DateTimeField("Дата и время начала отправки")
    end_time = models.DateTimeField("Дата и время окончания отправки")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE,
        related_name="mailings", verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient, related_name="mailings", verbose_name="Получатели",
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="mailings", verbose_name="Владелец",
        null=True, blank=True,
    )
    is_disabled = models.BooleanField("Отключена менеджером", default=False)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Рассылка #{self.pk} — {self.message.subject}"

    def clean(self):
        """Валидация: start_time не в прошлом, start_time < end_time."""
        if self.start_time and self.end_time:
            if self.start_time < timezone.now():
                raise ValidationError({"start_time": "Дата начала не может быть в прошлом."})
            if self.start_time >= self.end_time:
                raise ValidationError({"end_time": "Дата окончания должна быть позже даты начала."})

    @property
    def status(self):
        """Вычисляет статус динамически."""
        now = timezone.now()
        if now < self.start_time:
            return self.STATUS_CREATED
        elif now > self.end_time:
            return self.STATUS_COMPLETED
        else:
            return self.STATUS_STARTED

    @property
    def is_active(self):
        """Активна ли рассылка прямо сейчас."""
        return self.status == self.STATUS_STARTED and not self.is_disabled


class Attempt(models.Model):
    """Попытка отправки письма в рамках рассылки."""

    STATUS_SUCCESS = "Успешно"
    STATUS_FAILED = "Не успешно"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    attempt_time = models.DateTimeField("Дата и время попытки", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField("Ответ почтового сервера", blank=True)
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE,
        related_name="attempts", verbose_name="Рассылка",
    )

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"Попытка {self.attempt_time:%Y-%m-%d %H:%M} — {self.status}"
