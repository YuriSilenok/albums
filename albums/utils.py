import user_agents
from django.utils import timezone
from .models import ActivityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def parse_user_agent(user_agent_string):
    ua = user_agents.parse(user_agent_string)
    # Некоторые свойства могут быть None — приводим их к пустой строке,
    # чтобы избежать ошибок NOT NULL при сохранении в БД.
    def _safe(attr):
        return (attr or '')

    return {
        'browser_family': _safe(getattr(ua.browser, 'family', '')),
        'browser_version': _safe(getattr(ua.browser, 'version_string', '')),
        'os_family': _safe(getattr(ua.os, 'family', '')),
        'os_version': _safe(getattr(ua.os, 'version_string', '')),
        'device_family': _safe(getattr(ua.device, 'family', '')),
        'device_brand': _safe(getattr(ua.device, 'brand', '')),
        'device_model': _safe(getattr(ua.device, 'model', '')),
    }

def log_activity(request, action, user=None, album=None, media_file=None):
    ip = get_client_ip(request)
    user_agent_info = parse_user_agent(request.META.get('HTTP_USER_AGENT', ''))
    
    log_entry = ActivityLog(
        user=user,
        action=action,
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', ''),
        album=album,
        media_file=media_file,
        **user_agent_info
    )
    log_entry.save()
    return log_entry