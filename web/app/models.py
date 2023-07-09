from django.db import models
from django.contrib.auth.models import AbstractUser

from django_multitenant.models import TenantModel

from . import managers


class Account(TenantModel):
    name = models.CharField(max_length=128)
    site = models.URLField()

    class TenantMeta:
        tenant_field_name = 'id'


class User(AbstractUser):

    username = None
    email = models.EmailField(max_length=100, unique=True)
    account = models.ForeignKey(Account, related_name='users', on_delete=models.CASCADE, null=True, blank=True)
    objects = managers.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class TenantMeta:
        tenant_field_name = 'account_id'

    def __str__(self):
        return self.get_full_name()
