from celery import shared_task
from celery.utils.log import get_task_logger

from app.models import WatiAttribute
from app.services import WatiService


logger = get_task_logger(__name__)


@shared_task
def add():
    logger.info('Add called from scheduler-logger-info')


@shared_task
def update_wati_template():
    wati_attributes = WatiAttribute.objects.filter(connected=True)
    for wati_attribute in wati_attributes:
        WatiService.update_template_for_account(account=wati_attribute.account)
