from django.db import models


class VisitorQuerySet(models.QuerySet):
    def for_account(self, account):
        return self.filter(account=account)

    def with_analytics_for_account(self, account):
        from app.models import Analytics
        return self.for_account(account).prefetch_related(
            models.Prefetch('analytics', queryset=Analytics.objects.filter(account=account))
        )
