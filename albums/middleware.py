from .utils import log_activity

class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Логируем вход пользователя
        if request.user.is_authenticated and not hasattr(request, 'activity_logged'):
            log_activity(request, 'login', user=request.user)
            request.activity_logged = True
            
        return response