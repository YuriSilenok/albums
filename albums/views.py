from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, Http404
from django.db.models import Q
from .models import Album, MediaFile, ActivityLog
from .forms import AlbumForm, MediaUploadForm, AlbumAccessForm
from .utils import log_activity

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_activity(request, 'login', user=user)
            return redirect('album_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def album_list(request):
    albums = Album.objects.filter(owner=request.user)
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
    album = get_object_or_404(Album, id=album_id)
    
    # Проверка доступа
    if not check_album_access(request, album):
        return redirect('album_access', album_id=album.id)
    
    log_activity(request, 'album_view', 
                user=request.user if request.user.is_authenticated else None, 
                album=album)
    
    return render(request, 'albums/album_detail.html', {
        'album': album,
        'media_files': album.media_files.all()
    })

def album_access(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    
    if request.method == 'POST':
        form = AlbumAccessForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password', '')
            
            # Проверка пароля альбома
            if album.password and album.password == password:
                request.session[f'album_access_{album.id}'] = True
                return redirect('album_detail', album_id=album.id)
            
            # Проверка пароля для просмотра
            if album.view_password and album.view_password == password:
                request.session[f'album_view_{album.id}'] = True
                return redirect('album_detail', album_id=album.id)
            
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
    if request.session.get(f'album_view_{album.id}') or request.session.get(f'album_access_{album.id}'):
        return True
    
    # Публичный альбом с паролем просмотра
    if album.is_public and album.view_password:
        return False
    
    # Приватный альбом с паролем
    if album.password:
        return False
    
    return False

@login_required
def upload_media(request, album_id):
    album = get_object_or_404(Album, id=album_id, owner=request.user)
    
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