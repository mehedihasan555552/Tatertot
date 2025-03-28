from django.contrib import admin
from .models import Show, Episode, AppSettings

class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ['title', 'thumbnail_url', 'm3u8_url', 'order']

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title',)
    ordering = ('order',)
    inlines = [EpisodeInline]

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'show', 'order')
    list_filter = ('show',)
    search_fields = ('title', 'show__title')
    ordering = ('show', 'order')

@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_roku_publish', 'last_firetv_publish')
    
    def has_add_permission(self, request):
        # Prevent creating multiple AppSettings instances
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the AppSettings instance
        return False