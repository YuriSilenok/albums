import user_agents
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
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
    
    # Определяем content_object для универсальной связи
    content_type = None
    object_id = None
    
    # Приоритет: media_file > album
    if media_file:
        content_type = ContentType.objects.get_for_model(media_file)
        object_id = media_file.id
    elif album:
        content_type = ContentType.objects.get_for_model(album)
        object_id = album.id
    
    log_entry = ActivityLog(
        user=user,
        action=action,
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', ''),
        album=album,
        media_file=media_file,
        content_type=content_type,
        object_id=object_id,
        **user_agent_info
    )
    log_entry.save()
    return log_entry

def invalidate_album_sessions(album_id, exclude_session_key=None):
    """
    Invalidate all sessions that have access to an album.
    This is used when password is changed to force re-authentication.
    
    Args:
        album_id: UUID of the album
        exclude_session_key: Optional session key to exclude (e.g., owner's current session)
    """
    from django.contrib.sessions.models import Session
    import json
    
    session_keys_to_delete = []
    
    # Iterate through all active sessions
    for session in Session.objects.all():
        session_data = session.get_decoded()
        
        # Check if session has album access keys
        view_key = f'album_view_{album_id}'
        access_key = f'album_access_{album_id}'
        
        if view_key in session_data or access_key in session_data:
            # Skip owner's session if provided
            if exclude_session_key and session.session_key == exclude_session_key:
                continue
            
            session_keys_to_delete.append(session.session_key)
    
    # Delete sessions
    if session_keys_to_delete:
        Session.objects.filter(session_key__in=session_keys_to_delete).delete()