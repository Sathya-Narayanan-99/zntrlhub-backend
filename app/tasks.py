from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime

from app.models import WatiAttribute, Segmentation, Message
from app.services import WatiService, SegmentationService
from app.wati import Wati


logger = get_task_logger(__name__)


@shared_task
def update_wati_template():
    wati_attributes = WatiAttribute.objects.filter(connected=True)
    for wati_attribute in wati_attributes:
        WatiService.update_template_for_account(account=wati_attribute.account)

@shared_task
def sync_visitors_for_segmentation():
    segmentations = Segmentation.objects.all()
    for segmentation in segmentations:
        SegmentationService.update_visitor_segmentation_mapping(segmentation=segmentation)


@shared_task
def schedule_message(message_id: int, recievers: list):
    '''
    This function is invoked to schedule a message.
    '''
    message = Message.objects.get(id=message_id)
    account = message.campaign.account
    wati_attribute = WatiAttribute.objects.get_wati_attribute_for_account(account=account)

    if wati_attribute.connected:

        wati = Wati(**wati_attribute.get_api_credentials())
        wati.send_tempate_messages(
            template_name=message.template,
            broadcast_name=message.campaign.name,
            recievers=recievers,
            message=message
        )
