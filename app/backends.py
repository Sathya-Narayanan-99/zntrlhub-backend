from urllib.parse import urlparse
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.models import AnonymousUser

from app.tenant import set_current_account

from app.models import Account

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        authenticated_user = super().authenticate(request)

        if authenticated_user:
            user, jwt_value = authenticated_user
            set_current_account(user.account)
        else:
            site = request.META.get('HTTP_ORIGIN')
            if site:
                parsed_url = urlparse(site)
                site = parsed_url.netloc.strip()
            try:
                account = Account.objects.get(site=site)
                set_current_account(account)
                return AnonymousUser(), {}
            except Account.DoesNotExist:
                return None

        return authenticated_user
