from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import log_activity


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login event."""
    log_activity(request, 'login', user=user)
