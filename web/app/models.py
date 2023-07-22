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
    browser = models.CharField(max_length=64)
    device = models.CharField(max_length=64)

    page_name = models.CharField(max_length=128)
    page_url = models.URLField(max_length=2000)

    button_clicked = models.CharField(max_length=128)

    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=128)

    timezone = models.CharField(max_length=64)
    time_stayed = models.DurationField()

    created = models.DateTimeField(auto_now_add=True)

    account = models.ForeignKey(Account, related_name='analytics', on_delete=models.CASCADE)
    visitor = models.ForeignKey('Visitor', related_name='analytics', on_delete=models.CASCADE)


class Visitor(models.Model):
    name = models.CharField(max_length=64)
    whatsapp_number = models.CharField(max_length=32)
    device_uuid = models.UUIDField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    account = models.ManyToManyField(Account, related_name='visitors')

    objects = managers.VisitorManager()
