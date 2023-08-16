from django.core.management.base import BaseCommand
from django.db import transaction

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from app.tasks import add


class Command(BaseCommand):
    """
    Setup celery beat periodic tasks.
    """

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print('Deleting all periodic tasks and schedules...\n')

        PeriodicTask.objects.all().delete()
        CrontabSchedule.objects.all().delete()

        cron_every_5_minutes = CrontabSchedule.objects.create(
            minute='*/5',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'
        )

        periodic_tasks_data = [
            {
                'task': add,
                'name': 'Test for scheduling add method',
                'schedule': cron_every_5_minutes,
                'expire_seconds': 60
            }
        ]
        for periodic_task in periodic_tasks_data:
            print(f'Setting up {periodic_task["task"].name}')

            PeriodicTask.objects.create(
                name=periodic_task['name'],
                task=periodic_task['task'].name,
                crontab=periodic_task['schedule'],
                expire_seconds=periodic_task['expire_seconds'],
            )