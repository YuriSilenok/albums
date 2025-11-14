from django import forms
from .models import Album, MediaFile

class AlbumForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    view_password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = Album
        fields = ['title', 'description', 'password', 'is_public', 'view_password']

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file', 'description']

class AlbumAccessForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=False)