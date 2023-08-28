from urllib.parse import urlparse

from rest_framework.permissions import BasePermission
from app.tenant import get_current_account

class AnonymousFromRegisteredSitePermission(BasePermission):
    """
    Custom permission to allow only anonymous users from the sites registered to the account.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            current_account = get_current_account()
            if not current_account:
                return False

            site = request.META.get('HTTP_ORIGIN')
            if site:
                parsed_url = urlparse(site)
                site = parsed_url.netloc.strip()
            return site == current_account.site

        return False
