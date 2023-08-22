from django.db import models
from django.contrib.auth.models import AbstractUser

from . import managers


class Account(models.Model):
    name = models.CharField(max_length=128)
    site = models.CharField(max_length=256, unique=True)

    objects = managers.AccountManager()


class User(AbstractUser):

    username = None
    email = models.EmailField(max_length=100, unique=True)
    account = models.ForeignKey(Account, related_name='users', on_delete=models.CASCADE, null=True, blank=True)
    objects = managers.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name()


class Analytics(models.Model):
    browser = models.CharField(max_length=64, null=True, blank=True)
    device = models.CharField(max_length=64, null=True, blank=True)

    page_name = models.CharField(max_length=128, null=True, blank=True)
    page_url = models.URLField(max_length=2000, null=True, blank=True)

    button_clicked = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)

    timezone = models.CharField(max_length=64, null=True, blank=True)
    time_stayed = models.FloatField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    account = models.ForeignKey(Account, related_name='analytics', on_delete=models.CASCADE)
    visitor = models.ForeignKey('Visitor', related_name='analytics', on_delete=models.CASCADE)

    objects = managers.AnalyticsManager()


class Visitor(models.Model):
    name = models.CharField(max_length=64)
    whatsapp_number = models.CharField(max_length=32)
    device_uuid = models.UUIDField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    account = models.ManyToManyField(Account, related_name='visitors')

    objects = managers.VisitorManager()


class Segmentation(models.Model):
    name = models.CharField(max_length=64)
    rql_query = models.CharField(max_length=1000)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    account = models.ForeignKey(Account, related_name='segmentations', on_delete=models.CASCADE)

    objects = managers.SegmentationManager()


class WatiAttribute(models.Model):
    api_endpoint = models.URLField(max_length=2000)
    api_key = models.CharField(max_length=1000)

    connected = models.BooleanField(default=False)

    account = models.OneToOneField(Account, related_name='Wati_attribute', on_delete=models.CASCADE)

    objects = managers.WatiAttributeManager()

    def get_api_credentials(self):
        return {
        'api_endpoint': self.api_endpoint,
        'api_key': self.api_key
    }


class WatiTemplate(models.Model):
    template = models.JSONField(default=dict)

    account = models.ForeignKey(Account, related_name='wati_template', on_delete=models.CASCADE)

    objects = managers.WatiTemplateManager()
