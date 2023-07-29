from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from rest_framework import serializers

from app import custom_exceptions
from app.tenant import get_current_account

from .models import Account, Visitor, Analytics

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
