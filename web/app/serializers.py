from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Account

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'account']
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
        fields = ['id', 'name', 'site']

    def to_internal_value(self, data):
        site = data.get('site')
        if site:
            parsed_url = urlparse(site)
            domain = parsed_url.netloc
            data['site'] = domain
        return super().to_internal_value(data)
