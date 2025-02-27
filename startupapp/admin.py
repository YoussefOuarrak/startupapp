from django.contrib import admin
from .models import Startup, StartupApplication

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ("startup_id", "item_name", "pipeline", "location")
    search_fields = ("startup_id", "item_name")

# ✅ Inline display of applications inside Startup
class StartupApplicationInline(admin.TabularInline):
    model = StartupApplication
    extra = 1  # Allows adding new applications directly

@admin.register(StartupApplication)
class StartupApplicationAdmin(admin.ModelAdmin):
    list_display = ("application_id", "startup", "applicant_name", "submitted_at")
    search_fields = ("application_id", "startup__item_name", "applicant_name")
    list_filter = ("business_stage", "submitted_at")

# ✅ Link Applications to Startup Admin
class StartupAdmin(admin.ModelAdmin):
    list_display = ("startup_id", "item_name", "pipeline", "location")
    search_fields = ("startup_id", "item_name")
    inlines = [StartupApplicationInline]  # Show applications inside Startup
