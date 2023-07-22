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
