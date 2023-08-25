from django.core.management.base import BaseCommand
from django.db import transaction

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from app.tasks import update_wati_template, sync_visitors_for_segmentation


class Command(BaseCommand):
    """
    Setup celery beat periodic tasks.
    """

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print('Setting up all periodic tasks.')

        PeriodicTask.objects.all().delete()
        CrontabSchedule.objects.all().delete()

        cron_every_15_minutes = CrontabSchedule.objects.create(
            minute='*/15',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'
        )

        periodic_tasks_data = [
            {
                'task': update_wati_template,
                'name': 'Task to update wati templates',
                'schedule': cron_every_15_minutes,
                'expire_seconds': 60
            },
            {
                'task': sync_visitors_for_segmentation,
                'name': 'Task to sync visitors for segmentation',
                'schedule': cron_every_15_minutes,
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
