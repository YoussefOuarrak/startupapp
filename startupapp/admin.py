from django.contrib import admin
from .models import Startup

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ("startup_id", "item_name", "pipeline", "location")
    search_fields = ("startup_id", "item_name")
