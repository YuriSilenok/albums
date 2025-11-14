from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from albums import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/logout/', RedirectView.as_view(url='/logout/', permanent=False)),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('', views.album_list, name='home'),
    path('albums/', views.album_list, name='album_list'),
    path('albums/create/', views.create_album, name='create_album'),
    path('albums/<uuid:album_id>/', views.album_detail, name='album_detail'),
    path('albums/<uuid:album_id>/access/', views.album_access, name='album_access'),
    path('albums/<uuid:album_id>/upload/', views.upload_media, name='upload_media'),
    path('albums/<uuid:album_id>/edit/', views.edit_album, name='edit_album'),
    path('albums/<uuid:album_id>/delete/', views.delete_album, name='delete_album'),
    path('albums/<uuid:album_id>/media/<uuid:media_id>/delete/', views.delete_media, name='delete_media'),
    path('albums/<uuid:album_id>/media/<uuid:media_id>/', views.view_media, name='view_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)