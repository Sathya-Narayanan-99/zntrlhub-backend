from django.contrib.auth.models import BaseUserManager
from django.db import models

from app.tenant import get_current_account

class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        if not (extra_fields.get('first_name') and extra_fields.get('last_name')):
            raise ValueError("First name and last name are required.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)

    def get_users_for_account(self, account):
        return self.filter(account=account)


class AccountManager(models.Manager):

    use_in_migration = True

    def create_account(self, name, site):
        account = self.create(name=name, site=site)
        return account


class VisitorManager(models.Manager):

    use_in_migrations = True

    def create_visitor(self, name, whatsapp_number, device_uuid, account):
        visitor = self.create(name=name, whatsapp_number=whatsapp_number, device_uuid=device_uuid)
        visitor.account.add(account)
        return visitor

    def add_visitor_to_current_account(self, visitor):
        account = get_current_account()
        visitor.account.add(account)
        return visitor
