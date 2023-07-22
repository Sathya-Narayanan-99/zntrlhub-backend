from django.contrib.auth import get_user_model
from django.db import transaction

from app.tenant import get_current_account
from app.custom_exceptions import VisitorAlreadyReported, VisitorNotReported

from .serializers import (AccountSerializer, UserSerializer, VisitorSerializer,
                          AnalyticsSerializer)
from .models import Visitor

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
