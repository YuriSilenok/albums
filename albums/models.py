from django.db import models
from django.contrib.auth.models import User
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
    password = models.CharField(max_length=100, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    view_password = models.CharField(max_length=100, blank=True, null=True)

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

class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('album_create', 'Album Creation'),
        ('album_view', 'Album View'),
        ('media_upload', 'Media Upload'),
        ('media_view', 'Media View'),
        ('share_access', 'Share Access'),
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
        ]