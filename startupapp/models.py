from django.db import models

# Startup model
class Startup(models.Model):
    # Core Startup Data
    startup_id = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    pipeline = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    markets = models.TextField(null=True, blank=True)
    
    # Founders (structured as JSON for flexibility)
    founders = models.JSONField(default=list, blank=True)
    
    # Social Media Links
    social_media = models.JSONField(default=dict, blank=True)
    
    # Business Information
    tagline = models.TextField(null=True, blank=True)
    milestone = models.TextField(null=True, blank=True)
    revenue_model = models.TextField(null=True, blank=True)
    
    # Source Information
    sources = models.JSONField(default=list, blank=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    
    # Company Details
    incorporated = models.CharField(max_length=100, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    differentiators = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    interfaces = models.TextField(null=True, blank=True)
    
    # Financial Data as Text (to preserve currency symbols)
    total_funding_currency = models.CharField(max_length=3, null=True, blank=True)  # "GBP", "USD", etc.
    total_funding_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Numeric amount
    cash_runway = models.CharField(max_length=50, null=True, blank=True)
    rev_last_12_months = models.CharField(max_length=50, null=True, blank=True)
    rev_last_month = models.CharField(max_length=50, null=True, blank=True)
    rounds = models.IntegerField(null=True, blank=True)  # Rounds remain as integer
    
    # Related Data
    clients = models.TextField(null=True, blank=True)
    videos = models.TextField(null=True, blank=True)
    files = models.TextField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

    class Meta:
        indexes = [
            models.Index(fields=['startup_id']),
            models.Index(fields=['item_name']),
        ]

#StartupApplication model
class StartupApplication(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="applications")
    application_id = models.CharField(max_length=50, unique=True)
    applicant_name = models.CharField(max_length=255, null=True, blank=True)
    primary_contact_title = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    brief_description = models.TextField(null=True, blank=True) 
    funding_requested = models.CharField(max_length=50, null=True, blank=True)
    business_stage = models.CharField(max_length=100, null=True, blank=True)  # Renamed from "business_stage"
    average_score = models.FloatField(null=True, blank=True)  # Renamed from "quality_score"
    submitted_at = models.DateTimeField(auto_now_add=True)

    #Contact & Social Media
    contact_info = models.JSONField(default=dict, blank=True)

    #Video Links
    videos = models.JSONField(default=dict, blank=True)

    #Company Registration Info (Added "start_date")
    registration_info = models.JSONField(default=dict, blank=True)

    #Business Progress
    progress_status = models.JSONField(default=dict, blank=True)

    #Financial Data
    financials = models.JSONField(default=dict, blank=True)

    #Customers & Markets
    customer_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Application {self.application_id} for {self.startup.item_name}"

# ✅ Added UploadedFile Model
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
