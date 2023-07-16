from django.contrib.auth import get_user_model
from rest_framework import viewsets, views
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from app.serializers import UserSerializer, AccountSerializer
from app.services import AccountRegistrationService
from app.swagger_schemas import register_api_schema

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


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
