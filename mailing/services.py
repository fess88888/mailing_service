"""
Сервисный слой: отправка рассылок, бизнес-логика.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import Mailing, Attempt


def send_mailing(mailing):
    """
    Отправляет письма получателям рассылки.
    Возвращает кортеж (success_count, fail_count).

    Проверяет временно'е окно: отправка разрешена только если
    текущее время между start_time и end_time.
    """
    now = timezone.now()

    # Валидация временного окна
    if now < mailing.start_time:
        raise ValueError(
            f"Отправка невозможна: время начала рассылки — {mailing.start_time:%Y-%m-%d %H:%M}."
        )
    if now > mailing.end_time:
        raise ValueError(
            f"Отправка невозможна: время окончания рассылки — {mailing.end_time:%Y-%m-%d %H:%M}."
        )
    if mailing.is_disabled:
        raise ValueError("Рассылка отключена менеджером и не может быть отправлена.")

    success_count = 0
    fail_count = 0
    recipients = mailing.recipients.all()

    if not recipients:
        raise ValueError("У рассылки нет получателей.")

    message = mailing.message

    # Batch-создание записей о попытках
    attempts_to_create = []

    for recipient in recipients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts_to_create.append(Attempt(
                status=Attempt.STATUS_SUCCESS,
                server_response="Письмо успешно отправлено.",
                mailing=mailing,
            ))
            success_count += 1
        except Exception as e:
            attempts_to_create.append(Attempt(
                status=Attempt.STATUS_FAILED,
                server_response=str(e),
                mailing=mailing,
            ))
            fail_count += 1

    # Создаём все записи через batch (bulk_create)
    if attempts_to_create:
        Attempt.objects.bulk_create(attempts_to_create)

    return success_count, fail_count


def get_home_stats():
    """
    Возвращает статистику для главной страницы:
    - всего рассылок
    - активных рассылок
    - уникальных получателей
    """
    now = timezone.now()
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        is_disabled=False,
    ).count()
    total_recipients = Mailing.recipients.through.objects.values_list(
        "recipient_id", flat=True
    ).distinct().count()

    return {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "total_recipients": total_recipients,
    }
