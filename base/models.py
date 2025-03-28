from django.db import models

# Create your models here.
class Show(models.Model):
    """Represents a TV show with multiple episodes"""
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Episode(models.Model):
    """Represents an episode of a show"""
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=100)
    m3u8_url = models.CharField(max_length=500)
    thumbnail_url = models.CharField(max_length=500)
    duration= models.CharField(max_length=50,null=True,blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.show.title} - {self.title}"




class AppSettings(models.Model):
    """Stores global app settings for Roku and Fire TV separately"""
    
    # Roku Settings
    roku_background_image_url = models.URLField(max_length=500, blank=True)
    roku_splash_video_url = models.URLField(max_length=500, blank=True)
    last_roku_publish = models.DateTimeField(null=True, blank=True)
    
    # Fire TV Settings
    firetv_background_image_url = models.URLField(max_length=500, blank=True)
    firetv_splash_video_url = models.URLField(max_length=500, blank=True)
    last_firetv_publish = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "App Settings"
    
    def __str__(self):
        return "App Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create app settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings  
