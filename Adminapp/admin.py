from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'hours', 'created_at')
    search_fields = ('name', 'activity')
    list_filter = ('created_at',)
