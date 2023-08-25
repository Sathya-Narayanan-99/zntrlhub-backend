from django.contrib.auth.models import BaseUserManager
from django.db import models

from app.querysets import VisitorQuerySet
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

    def get_queryset(self):
        return VisitorQuerySet(self.model, using=self._db)

    def create_visitor(self, name, whatsapp_number, device_uuid, account):
        visitor = self.create(name=name, whatsapp_number=whatsapp_number, device_uuid=device_uuid)
        visitor.account.add(account)
        return visitor

    def add_visitor_to_current_account(self, visitor):
        account = get_current_account()
        visitor.account.add(account)
        return visitor

    def is_visitor_in_account(self, visitor, account):
        return visitor.account.filter(id=account.id).exists()

    def get_visitors_for_account(self, account):
        return self.get_queryset().for_account(account)

    def get_visitors_with_analytics_for_account(self, account):
        return self.get_queryset().with_analytics_for_account(account)


class AnalyticsManager(models.Manager):

    use_in_migrations = True

    def ingest_analytics(self, **analytics_data):
        analytics = self.create(**analytics_data)
        return analytics

    def get_analytics_for_account(self, account):
        return self.filter(account=account).prefetch_related('visitor')

    def get_distinct_page_names_for_account(self, account):
        return self.filter(account=account).values_list('page_name', flat=True).distinct()

    def get_distinct_button_clicked_for_account(self, account):
        return self.filter(account=account).exclude(button_clicked="").values_list('button_clicked', flat=True).distinct()

    def get_unique_visitor_for_account(self, account, query=None):
        queryset = self.get_analytics_for_account(account=account)
        if not query:
            return queryset

        from app.filters import AnalyticsFilters
        analytics_filter = AnalyticsFilters(queryset)
        _, filtered_queryset = analytics_filter.apply_filters(query=query)
        visitor_ids = [item['visitor'] for item in filtered_queryset.distinct('visitor').values('visitor')]

        return visitor_ids


class SegmentationManager(models.Manager):

    use_in_migrations = True

    def create_segmentation(self, **segmentation_data):
        segmentation = self.create(**segmentation_data)
        return segmentation

    def get_segmentation_for_account(self, account):
        return self.filter(account=account)


class WatiAttributeManager(models.Manager):

    use_in_migrations = True

    def get_wati_attribute_for_account(self, account):
        try:
            instance = self.get(account=account)
        except self.model.DoesNotExist:
            instance = self.create(account=account)
        return instance


class WatiTemplateManager(models.Manager):

    use_in_migrations = True

    def get_wati_template_for_account(self, account):
        return self.filter(account=account)
    
    def flush_wati_template_for_account(self, account):
        return self.get_wati_template_for_account(account=account).delete()
    

class CampaignManager(models.Manager):

    use_in_migrations = True

    def create_campaign(self, **campaign_data):
        campaign = self.create(**campaign_data)
        return campaign

    def get_campaign_for_account(self, account):
        return self.filter(account=account)
