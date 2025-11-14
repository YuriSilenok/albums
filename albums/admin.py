from django.contrib import admin
from django.db.models import Q
from .models import Album, MediaFile, ActivityLog, UserProfile

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp', 'ip_address', 'album', 'browser_family', 'os_family']
    list_filter = ['action', 'timestamp', 'browser_family', 'os_family', 'device_family']
    search_fields = ['user__username', 'ip_address', 'user_agent', 'album__title']
    readonly_fields = ['timestamp', 'ip_address', 'user_agent', 'referrer']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'timestamp', 'album', 'media_file')
        }),
        ('Техническая информация', {
            'fields': ('ip_address', 'user_agent', 'referrer')
        }),
        ('Информация об устройстве', {
            'fields': (
                'browser_family', 'browser_version', 
                'os_family', 'os_version',
                'device_family', 'device_brand', 'device_model'
            )
        }),
    )
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Поиск по различным техническим параметрам
        if search_term:
            queryset |= self.model.objects.filter(
                Q(ip_address__icontains=search_term) |
                Q(user_agent__icontains=search_term) |
                Q(browser_family__icontains=search_term) |
                Q(os_family__icontains=search_term) |
                Q(device_family__icontains=search_term) |
                Q(device_brand__icontains=search_term) |
                Q(device_model__icontains=search_term)
            )
        
        return queryset, use_distinct

class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'is_public', 'is_deleted', 'deleted_at']
    list_filter = ['is_public', 'is_deleted', 'created_at']
    search_fields = ['title', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'owner')
        }),
        ('Доступ и безопасность', {
            'fields': ('is_public', 'password', 'view_password')
        }),
        ('Статус удаления', {
            'fields': ('is_deleted', 'deleted_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['file', 'album', 'file_type', 'uploaded_at', 'is_deleted', 'deleted_at']
    list_filter = ['file_type', 'is_deleted', 'uploaded_at']
    search_fields = ['album__title', 'file']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('album', 'file', 'file_type', 'description')
        }),
        ('Статус удаления', {
            'fields': ('is_deleted', 'deleted_at')
        }),
        ('Метаданные', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Album, AlbumAdmin)
admin.site.register(MediaFile, MediaFileAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(UserProfile)