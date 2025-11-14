from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from albums import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.album_list, name='home'),
    path('albums/', views.album_list, name='album_list'),
    path('albums/create/', views.create_album, name='create_album'),
    path('albums/<uuid:album_id>/', views.album_detail, name='album_detail'),
    path('albums/<uuid:album_id>/access/', views.album_access, name='album_access'),
    path('albums/<uuid:album_id>/upload/', views.upload_media, name='upload_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)