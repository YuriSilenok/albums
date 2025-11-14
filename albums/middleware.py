from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .utils import log_activity

class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

# Логирование входа пользователя
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout event."""
    log_activity(request, 'logout', user=user)