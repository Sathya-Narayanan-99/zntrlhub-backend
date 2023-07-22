from django.contrib.auth import get_user_model
from rest_framework import viewsets, views
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from app import custom_permissions
from app.models import Account, Visitor
from app.serializers import UserSerializer, AccountSerializer, VisitorSerializer
from app.services import AccountRegistrationService, VisitorService
from app.swagger_schemas import register_api_schema

from app.tenant import get_current_account

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        queryset = User.objects.get_users_for_account(account=account).order_by('-date_joined')
        return queryset


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows account to be viewed.
    """
    model = Account
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        queryset = Account.objects.filter(id=account.id)
        return queryset


class RegisterAPIView(views.APIView):
    """
    API view for registering a new account and user.
    """

    permission_classes = [permissions.AllowAny]

    @register_api_schema
    def post(self, request):
        account_data = request.data.get('account')
        user_data = request.data.get('user')

        account_error, user_error, account, user = AccountRegistrationService.register(account_data, user_data)

        if account_error or user_error:
            response_data = {}
            if account_error:
                response_data['account'] = account_error
            if user_error:
                response_data['user'] = user_error
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'message': 'Account registered successfully.',
            'account': AccountSerializer(account).data,
            'user': UserSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class VisitorReportAPIView(views.APIView):
    """
    API view for reporting a visitor.
    """

    model = Visitor
    serializer = VisitorSerializer
    permission_classes = [custom_permissions.AnonymousFromRegisteredSitePermission]

    def post(self, request):
        
        visitor_data = request.data
        VisitorService.report_visitor(visitor_data=visitor_data)
        return Response({'detail': 'Visitor reported.'},
                        status=status.HTTP_200_OK)
