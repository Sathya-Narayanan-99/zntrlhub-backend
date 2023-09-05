from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from rest_framework import serializers
from py_rql.parser import RQLParser

from app import custom_exceptions
from app.tenant import get_current_account

from .models import (Account, Visitor, Analytics,
                     Segmentation, WatiAttribute,
                     WatiTemplate, Campaign, Message,
                     VisitorSegmentationMap)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def to_internal_value(self, data):
        site = data.get('site')
        if site:
            parsed_url = urlparse(site)
            domain = parsed_url.netloc
            data['site'] = domain
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        account = Account.objects.create_account(**validated_data)
        return account


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'

    def create(self, validated_data):
        visitor = Visitor.objects.create_visitor(**validated_data)
        return visitor

    def to_representation(self, instance):
        data = super().to_representation(instance)
        account = get_current_account()
        if Visitor.objects.is_visitor_in_account(visitor=instance, account=account):
            data['account'] = account.id
        else:
            del data['account']
        return data


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = '__all__'

    def validate(self, attrs):
        account = attrs.get('account')
        visitor = attrs.get('visitor')
        if not Visitor.objects.is_visitor_in_account(visitor, account):
            raise custom_exceptions.VisitorNotReported
        return super().validate(attrs)

    def create(self, validated_data):
        analytics = Analytics.objects.ingest_analytics(**validated_data)
        return analytics


class VisitorWithAnalyticsSerializer(VisitorSerializer):
    analytics = AnalyticsSerializer(many=True, read_only=True)


class AnalyticsWithVisitorSerializer(AnalyticsSerializer):
    visitor = VisitorSerializer(read_only=True)


class SegmentationSerializer(serializers.ModelSerializer):
    visitor_count = serializers.SerializerMethodField()
    class Meta:
        model = Segmentation
        fields = '__all__'

    def get_visitor_count(self, instance):
        count = VisitorSegmentationMap.objects.filter(segmentation=instance).count()
        return count

    def validate_rql_query(self, value):
        RQLParser.parse_query(value)
        # Exception is handled by custom exception handler
        return value

    def create(self, validated_data):
        segmentation = Segmentation.objects.create_segmentation(**validated_data)
        return segmentation


class WatiAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatiAttribute
        fields = '__all__'
        extra_kwargs = {
            'api_endpoint': {'write_only': True},
            'api_key': {'write_only': True}
        }


class WatiTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatiTemplate
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'
