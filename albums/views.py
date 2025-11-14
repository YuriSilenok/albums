from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.utils import timezone
from .models import Album, MediaFile, ActivityLog
from .forms import AlbumForm, MediaUploadForm, AlbumAccessForm
from .utils import log_activity, invalidate_album_sessions

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_activity(request, 'register', user=user)
            log_activity(request, 'login', user=user)
            return redirect('album_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def album_list(request):
    albums = Album.objects.filter(owner=request.user, is_deleted=False)
    log_activity(request, 'album_view', user=request.user)
    return render(request, 'albums/album_list.html', {'albums': albums})

@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            log_activity(request, 'album_create', user=request.user, album=album)
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm()
    return render(request, 'albums/create_album.html', {'form': form})

def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id, is_deleted=False)
    
    # Проверка доступа
    if not check_album_access(request, album):
        return redirect('album_access', album_id=album.id)
    
    log_activity(request, 'album_view', 
                user=request.user if request.user.is_authenticated else None, 
                album=album)
    
    return render(request, 'albums/album_detail.html', {
        'album': album,
        'media_files': album.media_files.filter(is_deleted=False)
    })

def album_access(request, album_id):
    album = get_object_or_404(Album, id=album_id, is_deleted=False)
    
    if request.method == 'POST':
        form = AlbumAccessForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password', '')
            
            # Проверка пароля для просмотра
            if album.view_password and album.view_password == password:
                request.session[f'album_view_{album.id}'] = True
                log_activity(request, 'password_view', album=album)
                return redirect('album_detail', album_id=album.id)
            
            # Логирование неудачной попытки ввода пароля
            log_activity(request, 'password_view', album=album)
            form.add_error('password', 'Неверный пароль')
    else:
        form = AlbumAccessForm()
    
    return render(request, 'albums/album_access.html', {
        'album': album,
        'form': form
    })

def check_album_access(request, album):
    # Владелец имеет полный доступ
    if request.user.is_authenticated and album.owner == request.user:
        return True
    
    # Публичный альбом без пароля
    if album.is_public and not album.view_password:
        return True
    
    # Проверка сессии для доступа к просмотру
    if request.session.get(f'album_view_{album.id}'):
        return True
    
    # Альбом защищён паролем просмотра - требует пароль
    if album.view_password:
        return False
    
    return False

@login_required
def upload_media(request, album_id):
    album = get_object_or_404(Album, id=album_id, owner=request.user, is_deleted=False)
    
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media_file = form.save(commit=False)
            media_file.album = album
            
            # Определение типа файла
            file_type = media_file.file.name.lower()
            if any(ext in file_type for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                media_file.file_type = 'image'
            elif any(ext in file_type for ext in ['.mp4', '.avi', '.mov', '.wmv']):
                media_file.file_type = 'video'
            
            media_file.save()
            log_activity(request, 'media_upload', user=request.user, album=album, media_file=media_file)
            return redirect('album_detail', album_id=album.id)
    else:
        form = MediaUploadForm()
    
    return render(request, 'albums/upload_media.html', {
        'form': form,
        'album': album
    })

@login_required
def delete_media(request, album_id, media_id):
    """Mark a media file as deleted."""
    album = get_object_or_404(Album, id=album_id, owner=request.user, is_deleted=False)
    media_file = get_object_or_404(MediaFile, id=media_id, album=album, is_deleted=False)
    
    if request.method == 'POST':
        media_file.is_deleted = True
        media_file.deleted_at = timezone.now()
        media_file.save()
        log_activity(request, 'media_view', user=request.user, album=album, media_file=media_file)
        return redirect('album_detail', album_id=album.id)
    
    return render(request, 'albums/delete_media.html', {
        'album': album,
        'media_file': media_file
    })

@login_required
def delete_album(request, album_id):
    """Mark an entire album as deleted."""
    album = get_object_or_404(Album, id=album_id, owner=request.user, is_deleted=False)
    
    if request.method == 'POST':
        album.is_deleted = True
        album.deleted_at = timezone.now()
        album.save()
        log_activity(request, 'album_delete', user=request.user, album=album)
        return redirect('album_list')
    
    return render(request, 'albums/delete_album.html', {
        'album': album,
        'media_count': album.media_files.filter(is_deleted=False).count()
    })

@login_required
def edit_album(request, album_id):
    """Edit album settings including passwords."""
    album = get_object_or_404(Album, id=album_id, owner=request.user, is_deleted=False)
    
    if request.method == 'POST':
        old_view_password = album.view_password
        
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            log_activity(request, 'album_edit', user=request.user, album=album)
            
            # Invalidate sessions if view_password changed
            new_album = Album.objects.get(id=album_id)
            if old_view_password != new_album.view_password:
                # Invalidate all other users' sessions for this album, 
                # except the current user's session
                invalidate_album_sessions(album_id, exclude_session_key=request.session.session_key)
            
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm(instance=album)
    
    return render(request, 'albums/edit_album.html', {
        'form': form,
        'album': album
    })

def get_album_share_url(request, album):
    """Generate full share URL for album."""
    return request.build_absolute_uri(f'/albums/{album.id}/')

def view_media(request, album_id, media_id):
    """View media file with logging."""
    album = get_object_or_404(Album, id=album_id, is_deleted=False)
    media_file = get_object_or_404(MediaFile, id=media_id, album=album, is_deleted=False)
    
    # Проверка доступа
    if not check_album_access(request, album):
        return redirect('album_access', album_id=album.id)
    
    # Логирование просмотра фото
    log_activity(request, 'media_view', 
                user=request.user if request.user.is_authenticated else None, 
                album=album, 
                media_file=media_file)
    
    # Редирект на файл
    return redirect(media_file.file.url)

@login_required
def logout_view(request):
    """Logout user and log the event."""
    log_activity(request, 'logout', user=request.user)
    logout(request)
    return redirect('home')