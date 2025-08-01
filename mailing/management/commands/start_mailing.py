from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.views import start_mailing
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускает указанную рассылку или все активные рассылки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mailing-id',
            type=int,
            help='ID конкретной рассылки для запуска',
        )
        parser.add_argument(
            '--all-active',
            action='store_true',
            help='Запустить все активные рассылки',
        )

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')
        all_active = options.get('all_active')

        if mailing_id:
            self.start_single_mailing(mailing_id)
        elif all_active:
            self.start_all_active_mailings()
        else:
            self.stdout.write(
                self.style.ERROR('Необходимо указать --mailing-id или --all-active')
            )

    def start_single_mailing(self, mailing_id):
        try:
            mailing = Mailing.objects.get(id=mailing_id)
            self.stdout.write(f'Запуск рассылки ID {mailing_id}...')
            result = start_mailing(mailing_id)
            self.print_result(result, mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Рассылка с ID {mailing_id} не найдена')
            )

    def start_all_active_mailings(self):
        active_mailings = Mailing.objects.filter(status='started')
        if not active_mailings.exists():
            self.stdout.write('Нет активных рассылок для запуска')
            return

        self.stdout.write(f'Найдено {active_mailings.count()} активных рассылок...')

        for mailing in active_mailings:
            self.stdout.write(f'Запуск рассылки ID {mailing.id}...')
            result = start_mailing(mailing.id)
            self.print_result(result, mailing.id)

    def print_result(self, result, mailing_id):
        if result.get('status') == 'error':
            self.stdout.write(
                self.style.ERROR(f'Ошибка при запуске рассылки ID {mailing_id}: {result["message"]}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка ID {mailing_id} завершена. '
                    f'Всего: {result["total"]}, '
                    f'Успешно: {result["success"]}, '
                    f'Ошибки: {result["failed"]}. '
                    f'Сообщение: {result["message"]}'
                )
            )
