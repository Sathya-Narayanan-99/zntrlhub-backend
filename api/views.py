from django.contrib.auth import get_user_model
from rest_framework import viewsets, views
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from app import custom_permissions
from app import filters
from app.viewsets import ServiceModelViewset
from app.models import (Account, Visitor, Analytics,
                        Segmentation, Campaign, Message)
from app.serializers import (UserSerializer, AccountSerializer, VisitorSerializer,
                             VisitorWithAnalyticsSerializer, AnalyticsSerializer,
                             AnalyticsWithVisitorSerializer, SegmentationSerializer,
                             CampaignSerializer, MessageSerializer, WatiTemplateSerializer)
from app.services import (AccountRegistrationService, VisitorService, AnalyticsService,
                          SegmentationService, WatiService, CampaignService, MessageService,
                          WatiTemplate)
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


class VisitorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows visitors to be viewed.

    If the query parameter 'analytics' is set to 'true', the response will include analytics
    data related to the visitors. Otherwise, only visitor data will be returned.
    """
    model = Visitor
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        analytics = self.request.query_params.get('analytics', 'false').lower()
        if analytics == 'true':
            queryset = Visitor.objects.get_visitors_with_analytics_for_account(account)
        else:
            queryset = Visitor.objects.get_visitors_for_account(account)
        return queryset

    def get_serializer_class(self):
        analytics = self.request.query_params.get('analytics', 'false').lower()
        if analytics == 'true':
            serializer_class = VisitorWithAnalyticsSerializer
        else:
            serializer_class = VisitorSerializer
        return serializer_class


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows analytics to be viewed.
    """
    model = Analytics
    serializer_class = AnalyticsWithVisitorSerializer
    permission_classes = [permissions.IsAuthenticated]
    rql_filter_class = filters.AnalyticsFilters

    def get_queryset(self):
        account = get_current_account()
        queryset = Analytics.objects.get_analytics_for_account(account)
        return queryset

    @action(detail=False, methods=['GET'], rql_filter_class=[])
    def distinct_page_names(self, request):
        account = get_current_account()
        page_names = Analytics.objects.get_distinct_page_names_for_account(account=account)
        return Response(data=page_names)

    @action(detail=False, methods=['GET'], rql_filter_class=[])
    def distinct_button_clicked(self, request):
        account = get_current_account()
        button_clicked = Analytics.objects.get_distinct_button_clicked_for_account(account=account)
        return Response(data=button_clicked)


class SegmentationViewset(ServiceModelViewset):
    model = Segmentation
    serializer_class = SegmentationSerializer
    service_class = SegmentationService
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        queryset = Segmentation.objects.get_segmentation_for_account(account=account)
        return queryset


class CampaignViewset(ServiceModelViewset):
    model = Campaign
    serializer_class = CampaignSerializer
    service_class = CampaignService
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        queryset = Campaign.objects.get_campaign_for_account(account=account)
        return queryset


class MessageViewset(ServiceModelViewset):
    model = Message
    serializer_class = MessageSerializer
    service_class = MessageService
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        return self.model.objects.filter(campaign__account=account)
    

class TemplateViewset(viewsets.ReadOnlyModelViewSet):
    model = WatiTemplate
    serializer_class = WatiTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_current_account()
        return self.model.objects.filter(account=account)


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
    serializer_class = VisitorSerializer
    permission_classes = [custom_permissions.AnonymousFromRegisteredSitePermission]

    def post(self, request):

        visitor_data = request.data
        VisitorService.report_visitor(visitor_data=visitor_data)
        return Response({'detail': 'Visitor reported.'},
                        status=status.HTTP_200_OK)


class AnalyticsIngestionAPIView(views.APIView):
    """
    API view for ingesting analytics.
    """

    model = Analytics
    serializer_class = AnalyticsSerializer
    permission_classes = [custom_permissions.AnonymousFromRegisteredSitePermission]

    def post(self, request):
        analytics_data = request.data
        AnalyticsService.ingest_analytics(analytics_data=analytics_data)
        return Response({'detail': 'Analytics data ingested.'},
                        status=status.HTTP_200_OK)


class WatiAuthAPIView(views.APIView):
    """
    API View for authentication with wati
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        api_endpoint = request.data.get('api_endpoint')
        api_key = request.data.get('api_key')
        if not api_endpoint:
            return Response({'detail':'api_endpoint is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not api_key:
            return Response({'detail':'api_key is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        WatiService.update_credentials(api_endpoint=api_endpoint,
                                                            api_key=api_key)
        return Response({'detail':'Updated the credentials'},
                            status=status.HTTP_200_OK)


# class WatiEventsAPIView(views.APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         WatiService.process_wati_event(request.data)
#         return Response(status=status.HTTP_200_OK)
