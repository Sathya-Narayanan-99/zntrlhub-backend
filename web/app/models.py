from django.db import models
from django.contrib.auth.models import AbstractUser

from . import managers

class User(AbstractUser):

    username = None
    email = models.EmailField(max_length=100, unique=True)
    objects = managers.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name()
