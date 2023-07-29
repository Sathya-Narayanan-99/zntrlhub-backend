try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()

def set_current_account(account):
    """
    Utils to set a account in the current thread.
    Often used in a middleware once a user is logged in to make sure all db
    calls are sharded to the current account.
    Can be used by doing:
    ```
        get_current_account(my_class_object)
    ```
    """
    setattr(_thread_locals, "account", account)

def get_current_account():
    """
    Utils to get the account that hass been set in the current thread using `set_current_account`.
    Can be used by doing:
    ```
        my_class_object = get_current_account()
    ```
    Will return None if the account is not set
    """
    return getattr(_thread_locals, "account", None)
