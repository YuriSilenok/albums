from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    view_password = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class MediaFile(models.Model):
    FILE_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to='media/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('album_create', 'Album Creation'),
        ('album_edit', 'Album Edit'),
        ('album_view', 'Album View'),
        ('album_delete', 'Album Delete'),
        ('media_upload', 'Media Upload'),
        ('media_view', 'Media View'),
        ('password_view', 'Password View Attempt'),
        ('password_edit', 'Password Edit Attempt'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    media_file = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Универсальная связь с моделью контента (для расширяемости)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content_url = models.URLField(blank=True, null=True, help_text='URL на контент (альбом или файл)')
    
    # Дополнительная техническая информация
    browser_family = models.CharField(max_length=100, blank=True)
    browser_version = models.CharField(max_length=50, blank=True)
    os_family = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    device_family = models.CharField(max_length=100, blank=True)
    device_brand = models.CharField(max_length=50, blank=True)
    device_model = models.CharField(max_length=50, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['album']),
            models.Index(fields=['media_file']),
        ]