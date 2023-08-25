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

    def get_campaigns(self):
        return self.campaigns.all()


class VisitorSegmentationMap(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    segmentation = models.ForeignKey(Segmentation, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('visitor', 'segmentation')


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


class WatiMessage(models.Model):
    wati_message_id = models.CharField(max_length=128, null=True, default=None)

    message = models.ForeignKey('Message', related_name='wati_messages', on_delete=models.CASCADE)

    visitor = models.ForeignKey(Visitor, related_name='wati_messages', on_delete=models.CASCADE)


class Campaign(models.Model):

    ACTIVE_STATE = 'A'
    INACTIVE_STATE = 'I'
    STATE_CHOICES = (
        (ACTIVE_STATE, 'Active'),
        (INACTIVE_STATE, 'Inactive')
    )

    name = models.CharField(max_length=128)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ACTIVE_STATE)

    segment = models.ForeignKey(Segmentation, related_name='campaigns', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='campaigns', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = managers.CampaignManager()


class Message(models.Model):
    MESSAGE_HEAD = 0
    ON_MESSAGE_DELIVERED = 1
    ON_MESSAGE_READ = 2
    ON_MESSAGE_REPLIED = 3
    NODE_ACTION_CHOICES = (
        (MESSAGE_HEAD, 'Starting message'),
        (ON_MESSAGE_DELIVERED, 'On message delivered'),
        (ON_MESSAGE_READ, 'ON message read'),
        (ON_MESSAGE_REPLIED, 'On message replied')
    )
    action = models.IntegerField(choices=NODE_ACTION_CHOICES, default=MESSAGE_HEAD)
    schedule = models.IntegerField(null=True, default=1)

    template = models.CharField(max_length=1024)

    parent = models.ForeignKey('self', related_name='child_messages', on_delete=models.CASCADE, null=True)

    campaign = models.ForeignKey(Campaign, related_name='messages', on_delete=models.CASCADE)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('parent', 'action',)

    def get_head_message(self):
        head = self
        parent = self.parent
        while parent is not None:
            head = parent
            parent = parent.parent
        return head

    def get_descendants(self):
        descendants = Message.objects.filter(parent=self)
        return descendants

    def get_descendants_for_action_performed(self, action: int):
        descendants = Message.objects.filter(parent=self, action=action)
        return descendants

    def get_ancestors(self):
        ancestors = []
        parent = self.parent
        while parent is not None:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors
