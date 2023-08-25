from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import transaction

from app.tenant import get_current_account
from app.custom_exceptions import VisitorAlreadyReported, VisitorNotReported, WatiConnectionError
from app.wati import Wati

from .serializers import (AccountSerializer, UserSerializer, VisitorSerializer,
                          AnalyticsSerializer, SegmentationSerializer, WatiAttributeSerializer,
                          CampaignSerializer, MessageSerializer)
from .models import Analytics, Visitor, Message, WatiAttribute, WatiTemplate, WatiMessage, VisitorSegmentationMap

User = get_user_model()

class AccountRegistrationService:
    @classmethod
    @transaction.atomic
    def register(cls, account_data, user_data):
        account_serializer = AccountSerializer(data=account_data)
        user_serializer = UserSerializer(data=user_data)

        account_error, user_error = None, None

        if not account_serializer.is_valid():
            account_error = account_serializer.errors
        if not user_serializer.is_valid():
            user_error = user_serializer.errors

        if account_error or user_error:
            return account_error, user_error, None, None

        account = account_serializer.save()
        user = user_serializer.save(account=account)
        
        return None, None, account, user


class VisitorService:
    @classmethod
    def report_visitor(cls, visitor_data):
        account = get_current_account()
        visitor_data['account'] = [account.id]
        visitor_serializer = VisitorSerializer(data=visitor_data)
        visitor_serializer.is_valid(raise_exception=True)

        device_uuid = visitor_serializer.validated_data.get('device_uuid')

        try:
            visitor = Visitor.objects.prefetch_related('account').get(device_uuid=device_uuid)
            if not Visitor.objects.is_visitor_in_account(visitor, account):
                Visitor.objects.add_visitor_to_current_account(visitor=visitor)
            else:
                raise VisitorAlreadyReported
        except Visitor.DoesNotExist:
            visitor = visitor_serializer.save(account=account)

        return visitor


class AnalyticsService:
    @classmethod
    def ingest_analytics(cls, analytics_data):
        device_uuid = analytics_data.get('device_uuid')
        try:
            visitor = Visitor.objects.get(device_uuid=device_uuid)
        except Visitor.DoesNotExist:
            raise VisitorNotReported
        account = get_current_account()

        analytics_data['visitor'] = visitor.id
        analytics_data['account'] = account.id

        analytics_serializer = AnalyticsSerializer(data=analytics_data)
        analytics_serializer.is_valid(raise_exception=True)

        analytics = analytics_serializer.save()

        return analytics


class CampaignService:
    @classmethod
    def create(cls, data):
        account = get_current_account()
        data['account'] = account.id

        campaign_serializer = CampaignSerializer(data=data)
        campaign_serializer.is_valid(raise_exception=True)

        campaign = campaign_serializer.save()

        return campaign

    @classmethod
    def update(cls, instance, data, partial=False):
        account = get_current_account()
        data['account'] = account.id

        campaign_serializer = CampaignSerializer(instance, data=data, partial=partial)
        campaign_serializer.is_valid(raise_exception=True)

        campaign = campaign_serializer.save()

        return campaign

    @classmethod
    def delete(cls, instance):
        instance.delete()

    @classmethod
    def schedule_initial_message(cls, campaign, visitors):
        if not campaign.messages.first():
            return
        message = campaign.messages.first().get_head_message()
        MessageService.schedule_message(
            message=message,
            receivers=WatiService.get_recievers_for_visitors(visitors)
        )


class SegmentationService:
    @classmethod
    def create(cls, data):
        account = get_current_account()
        data['account'] = account.id

        segmentation_serializer = SegmentationSerializer(data=data)
        segmentation_serializer.is_valid(raise_exception=True)

        segmentation = segmentation_serializer.save()

        from app.tasks import sync_visitors_for_segmentation
        sync_visitors_for_segmentation.delay()

        return segmentation

    @classmethod
    def update(cls, instance, data, partial=False):
        account = get_current_account()
        data['account'] = account.id

        segmentation_serializer = SegmentationSerializer(instance, data=data, partial=partial)
        segmentation_serializer.is_valid(raise_exception=True)

        segmentation = segmentation_serializer.save()

        return segmentation

    @classmethod
    def delete(cls, instance):
        instance.delete()

    @classmethod
    def update_visitor_segmentation_mapping(cls, segmentation):
        visitors = Analytics.objects.get_unique_visitor_for_account(account=segmentation.account,
                                                                    query=segmentation.rql_query)
        visitor_segmentation_map_objs = []
        created_objs = []
        for visitor in visitors:
            visitor_segmentation_map, created = VisitorSegmentationMap.objects.get_or_create(visitor_id=visitor,
                                                                                        segmentation=segmentation)
            visitor_segmentation_map_objs.append(visitor_segmentation_map)
            if created:
                created_objs.append(visitor_segmentation_map)
        # VisitorSegmentationMap.objects.exclude(pk__in=[obj.pk for obj in visitor_segmentation_map_objs]).delete()

        for campaign in segmentation.get_campaigns():
            CampaignService.schedule_initial_message(
                campaign=campaign,
                visitors=[obj.visitor for obj in created_objs]
            )

        return visitor_segmentation_map_objs


class WatiService:
    @classmethod
    def update_credentials(cls, api_endpoint, api_key):
        account = get_current_account()

        data = {
            'api_endpoint': api_endpoint,
            'api_key': api_key
        }

        instance = WatiAttribute.objects.get_wati_attribute_for_account(account=account)

        wati_attribute_serializer = WatiAttributeSerializer(instance, data=data, partial=True)
        wati_attribute_serializer.is_valid(raise_exception=True)
        wati_attribute_serializer.save()
        instance = wati_attribute_serializer.instance

        WatiService.update_connection_status(wati_attribute=instance, raise_exception=True)

        return instance

    @classmethod
    def update_connection_status(cls, wati_attribute, commit=True, raise_exception=False):
        status = WatiService.get_connection_status(wati_attribute=wati_attribute)
        wati_attribute.connected = status

        if commit:
            wati_attribute.save()

        if raise_exception:
            if status is False:
                raise WatiConnectionError

        from app.tasks import update_wati_template
        update_wati_template.delay()

        return wati_attribute

    @classmethod
    def get_connection_status(cls, wati_attribute):
        wati = Wati(**wati_attribute.get_api_credentials())
        return wati.get_connection_status()
    
    @classmethod
    def update_template_for_account(cls, account=None):
        if not account:
            account = get_current_account()

        WatiTemplate.objects.flush_wati_template_for_account(account=account)

        wati_attribute = WatiAttribute.objects.get_wati_attribute_for_account(account=account)
        wati = Wati(**wati_attribute.get_api_credentials())

        page_number = 1
        all_templates = []
        while True:
            templates = wati.get_templates(page_number=page_number)

            if not templates:
                break

            all_templates.extend(templates)
            page_number += 1

        instances = []
        for template in all_templates:
            instance = WatiTemplate(template=template, account=account)
            instances.append(instance)

        WatiTemplate.objects.bulk_create(instances)

    @classmethod
    def process_wati_event(cls, event_body):
        event_type = event_body.get('eventType')
        if event_type == 'sentMessageDELIVERED':
            WatiService.process_message_delivered(event_body)
        elif event_type == 'sentMessageREAD':
            WatiService.process_message_delivered(event_body)

    @classmethod
    def process_message_delivered(cls, event_body):
        wati_message_id = event_body.get('whatsappMessageId')
        try:
            wati_message = WatiMessage.objects.get(wati_message_id=wati_message_id)
        except WatiMessage.DoesNotExist:
            return
        if wati_message.message.action == Message.ON_MESSAGE_DELIVERED:
            messages = wati_message.message.get_descendants_for_action_performed(Message.ON_MESSAGE_DELIVERED)
            for message in messages:
                MessageService.schedule_message(
                    message,
                    WatiService.get_recievers_for_visitors(wati_message.visitor)
                )

    @classmethod
    def process_message_read(cls, event_body):
        wati_message_id = event_body.get('whatsappMessageId')
        try:
            wati_message = WatiMessage.objects.get(wati_message_id=wati_message_id)
        except WatiMessage.DoesNotExist:
            return
        if wati_message.message.action == Message.ON_MESSAGE_READ:
            messages = wati_message.message.get_descendants_for_action_performed(Message.ON_MESSAGE_READ)
            for message in messages:
                MessageService.schedule_message(
                    message,
                    WatiService.get_recievers_for_visitors(wati_message.visitor)
                )
    
    @classmethod
    def process_message_replied(cls, event_body):
        wati_message_id = event_body.get('whatsappMessageId')
        try:
            wati_message = WatiMessage.objects.get(wati_message_id=wati_message_id)
        except WatiMessage.DoesNotExist:
            return
        if wati_message.message.action == Message.ON_MESSAGE_REPLIED:
            messages = wati_message.message.get_descendants_for_action_performed(Message.ON_MESSAGE_REPLIED)
            for message in messages:
                MessageService.schedule_message(
                    message,
                    WatiService.get_recievers_for_visitors(wati_message.visitor)
                )

    @classmethod
    def get_recievers_for_visitors(cls, visitors):
        receivers = []
        for visitor in visitors:
            receiver = {
                "whatsappNumber": visitor.whatsapp_number,
                "customParams": [
                    {
                    "name": "name",
                    "value": visitor.name,
                    },
                    {
                    "name": "phone",
                    "value": visitor.whatsapp_number,
                    }
                ]
            }
            receivers.append(receiver)
        return receivers


class MessageService:
    @classmethod
    def create(cls, data):
        message_serializer = MessageSerializer(data=data)
        message_serializer.is_valid(raise_exception=True)

        message = message_serializer.save()

        if message.action == Message.MESSAGE_HEAD:
            visitor_segmentation_map = VisitorSegmentationMap.objects.filter(segmentation=message.campaign.segment)
            CampaignService.schedule_initial_message(
                campaign=message.campaign,
                visitors=[obj.visitor for obj in visitor_segmentation_map]
            )

        return message

    @classmethod
    def delete(cls, instance):
        instance.delete()

    @classmethod
    def schedule_message(cls, message, receivers):
        eta = timezone.now() + timedelta(minutes=message.schedule)
        from app.tasks import schedule_message
        schedule_message.apply_async([message.id, receivers], eta=eta)
