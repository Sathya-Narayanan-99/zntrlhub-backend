from django.contrib.auth import get_user_model
from django.db import transaction

from .serializers import AccountSerializer, UserSerializer

from .models import Account

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

        validated_account_data = account_serializer.validated_data
        validated_user_data = user_serializer.validated_data

        account = Account.objects.create_account(**validated_account_data)
        user = User.objects.create_user(**validated_user_data, account=account)
        return None, None, account, user
