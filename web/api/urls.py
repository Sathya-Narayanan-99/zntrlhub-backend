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

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework')),

    path('register/', views.RegisterAPIView.as_view(), name='register-view'),
    path('visitor/report/', views.VisitorReportAPIView.as_view(), name='visitor-report'),

    path('', include(router.urls)),
]
