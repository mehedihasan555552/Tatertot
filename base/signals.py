from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Episode, AppSettings

@receiver(post_save, sender=Episode)
def update_splash_and_background(sender, instance, created, **kwargs):
    """Automatically update splash video and background image when a new episode is added"""
    if created:  # Only update if a new episode is created
        app_settings = AppSettings.get_settings()

        # Update Roku background image if it's empty
        if not app_settings.roku_background_image_url and instance.thumbnail_url:
            app_settings.roku_background_image_url = instance.thumbnail_url

        # Update Roku splash video if it's empty
        if not app_settings.roku_splash_video_url and instance.m3u8_url:
            app_settings.roku_splash_video_url = instance.m3u8_url

        # Update Fire TV background image if it's empty
        if not app_settings.firetv_background_image_url and instance.thumbnail_url:
            app_settings.firetv_background_image_url = instance.thumbnail_url

        # Update Fire TV splash video if it's empty
        if not app_settings.firetv_splash_video_url and instance.m3u8_url:
            app_settings.firetv_splash_video_url = instance.m3u8_url

        app_settings.save()
