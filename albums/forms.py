from django import forms
from .models import Album, MediaFile


class AlbumForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    view_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Album
        fields = ['title', 'description', 'password', 'is_public', 'view_password']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'view_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AlbumAccessForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)