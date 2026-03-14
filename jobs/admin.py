from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "stream", "is_active", "created_at")
    list_filter = ("stream", "is_active")
    search_fields = ("title", "company")