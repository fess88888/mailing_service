"""
Команда для отправки активных рассылок.
Использование: python manage.py send_mailings
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Отправляет все активные рассылки (в пределах временного окна)."

    def handle(self, *args, **options):
        now = timezone.now()
        active_mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_disabled=False,
        )
        if not active_mailings:
            self.stdout.write("Нет активных рассылок для отправки.")
            return

        for mailing in active_mailings:
            try:
                success, fail = send_mailing(mailing)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Рассылка #{mailing.pk}: отправлено {success}, ошибок {fail}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Рассылка #{mailing.pk}: {e}")
                )
