from django.utils import timezone
from django.db import models

class Startup(models.Model):
    """Represents a startup with business, financial, and contact details."""
    
    # Core information
    startup_id = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    pipeline = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    markets = models.TextField(null=True, blank=True)
    
    # Founders (stored as JSON for flexibility)
    founders = models.JSONField(default=list, blank=True)
    
    # Social media and contact links
    social_media = models.JSONField(default=dict, blank=True)
    
    # Business-related information
    tagline = models.TextField(null=True, blank=True)
    milestone = models.TextField(null=True, blank=True)
    revenue_model = models.TextField(null=True, blank=True)
    sources = models.JSONField(default=list, blank=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    
    # Company details
    incorporated = models.CharField(max_length=100, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    differentiators = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    interfaces = models.TextField(null=True, blank=True)
    
    # Financial details
    total_funding_currency = models.CharField(max_length=3, null=True, blank=True)  # Example: "USD"
    total_funding_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    cash_runway = models.CharField(max_length=50, null=True, blank=True)
    rev_last_12_months = models.CharField(max_length=50, null=True, blank=True)
    rev_last_month = models.CharField(max_length=50, null=True, blank=True)
    rounds = models.IntegerField(null=True, blank=True)
    
    # Additional related data
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

class StartupApplication(models.Model):
    """Represents an application submitted by a startup."""
    
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="applications")
    application_id = models.CharField(max_length=50, unique=True)
    applicant_name = models.CharField(max_length=255, null=True, blank=True)
    primary_contact_title = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    brief_description = models.TextField(null=True, blank=True)
    funding_requested = models.CharField(max_length=50, null=True, blank=True)
    business_stage = models.CharField(max_length=100, null=True, blank=True)
    average_score = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Structured fields for additional details
    contact_info = models.JSONField(default=dict, blank=True)
    videos = models.JSONField(default=dict, blank=True)
    registration_info = models.JSONField(default=dict, blank=True)
    progress_status = models.JSONField(default=dict, blank=True)
    financials = models.JSONField(default=dict, blank=True)
    customer_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Application {self.application_id} for {self.startup.item_name}"

class UploadedFile(models.Model):
    """Stores uploaded files for processing."""
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

class StartupAIAnalysis(models.Model):
    startup = models.OneToOneField('Startup', on_delete=models.CASCADE, related_name='ai_analysis')
    summary = models.TextField(blank=True, null=True)
    industry_classification = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"AI Analysis for {self.startup.item_name}"
