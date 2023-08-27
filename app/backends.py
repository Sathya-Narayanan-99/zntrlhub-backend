from rest_framework_simplejwt.authentication import JWTAuthentication
from app.tenant import set_current_account

from app.models import Account

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        authenticated_user = super().authenticate(request)

        if authenticated_user:
            user, jwt_value = authenticated_user
            set_current_account(user.account)
        else:
            site = request.get_host()
            try:
                account = Account.objects.get(site=site)
                set_current_account(account)
            except Account.DoesNotExist:
                return None

        return authenticated_user
