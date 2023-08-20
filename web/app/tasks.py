from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def add():
    logger.info('Add called from scheduler-logger-info')
