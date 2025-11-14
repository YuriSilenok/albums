from django import forms
from .models import Album, MediaFile


class AlbumForm(forms.ModelForm):
    view_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Пароль для просмотра'
    )

    class Meta:
        model = Album
        fields = ['title', 'description', 'view_password', 'is_public']
        labels = {
            'title': 'Название альбома',
            'description': 'Описание',
            'is_public': 'Публичный альбом',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'view_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable view_password field when album is public
        if self.instance and self.instance.is_public:
            self.fields['view_password'].disabled = True
            self.fields['view_password'].help_text = 'Пароль недоступен для публичных альбомов'


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file', 'description']
        labels = {
            'file': 'Файл',
            'description': 'Описание',
        }
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AlbumAccessForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Пароль для доступа'
    )