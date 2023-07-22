from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Account, Visitor

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
