from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'account', views.AccountViewSet, basename='account')
router.register(r'visitor', views.VisitorViewSet, basename='visitor')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
router.register(r'segmentations', views.SegmentationViewset, basename='segmentations')
router.register(r'campaigns', views.CampaignViewset, basename='campaigns')
router.register(r'messages', views.MessageViewset, basename='messages')
router.register(r'templates', views.TemplateViewset, basename='templates')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework')),

    path('register/', views.RegisterAPIView.as_view(), name='register-view'),
    path('visitor/report/', views.VisitorReportAPIView.as_view(), name='visitor-report'),
    path('analytics/ingest/', views.AnalyticsIngestionAPIView.as_view(), name='analytics-ingest'),

    path('wati/auth/', views.WatiAuthAPIView.as_view(), name='wati-auth'),
    # path('wati/events/', views.WatiEventsAPIView.as_view(), name='wati-events'),

    path('', include(router.urls)),
]
