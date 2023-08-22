from django.contrib.auth import get_user_model
from django.db import transaction

from app.tenant import get_current_account
from app.custom_exceptions import VisitorAlreadyReported, VisitorNotReported, WatiConnectionError
from app.wati import Wati

from .serializers import (AccountSerializer, UserSerializer, VisitorSerializer,
                          AnalyticsSerializer, SegmentationSerializer, WatiAttributeSerializer)
from .models import Visitor, WatiAttribute, WatiTemplate

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


class SegmentationService:
    @classmethod
    def create(cls, data):
        account = get_current_account()
        data['account'] = account.id

        segmentation_serializer = SegmentationSerializer(data=data)
        segmentation_serializer.is_valid(raise_exception=True)

        segmentation = segmentation_serializer.save()

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
