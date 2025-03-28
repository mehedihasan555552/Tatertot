from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ShowForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., TaterTot Adventures'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

        

class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ['title', 'show', 'm3u8_url', 'thumbnail_url', 'duration', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Episode 1: The Big Day'}),
            'show': forms.Select(attrs={'class': 'form-select'}),
            'm3u8_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g., https://viloud.tv/xxxx/playlist.m3u8'}),
            'thumbnail_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g., https://irp.cdn-website.com/.../image.png'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5.00'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

# class AppSettingsForm(forms.ModelForm):
#     class Meta:
#         model = AppSettings
#         fields = ['background_image_url', 'splash_video_url']
#         widgets = {
#             'background_image_url': forms.URLInput(attrs={'class': 'form-control', 'id': 'id_background_image_url', 'placeholder': 'e.g., https://example.com/background.jpg'}),
#             'splash_video_url': forms.URLInput(attrs={'class': 'form-control', 'id': 'id_splash_video_url', 'placeholder': 'e.g., https://example.com/splash.mp4'}),
#         }



class AppSettingsForm(forms.ModelForm):
    class Meta:
        model = AppSettings
        fields = [
            # Roku
            'roku_background_image_url',
            'roku_splash_video_url',

            # Fire TV
            'firetv_background_image_url',
            'firetv_splash_video_url',
        ]



class PublishForm(forms.Form):
    PLATFORM_CHOICES = [
        ('roku', 'Roku'),
        ('firetv', 'Fire TV'),
        ('both', 'Both Platforms'),
    ]
    platform = forms.ChoiceField(choices=PLATFORM_CHOICES, required=True)