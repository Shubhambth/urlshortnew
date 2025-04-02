from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import string
import random

def generate_short_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

class URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=50, unique=True, default=generate_short_code)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    click_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.original_url} -> {self.short_code}"

    class Meta:
        ordering = ['-created_at']

class URLAccess(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name='accesses')
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device_type = models.CharField(max_length=20, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    earnings = models.DecimalField(max_digits=5, decimal_places=3, default=0)

    class Meta:
        ordering = ['-accessed_at']

    def calculate_earnings(self):
        try:
            country_tier = CountryTier.objects.get(country=self.country)
            return country_tier.rate_per_click
        except CountryTier.DoesNotExist:
            # Default rate for unknown countries (Tier 3)
            return 0.001

    def save(self, *args, **kwargs):
        self.earnings = self.calculate_earnings()
        super().save(*args, **kwargs)

class DailyClickCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    click_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

class PaymentRequest(models.Model):
    PAYMENT_METHODS = [
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('mobile', 'Mobile Money'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(5)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.payment_method}"

class CountryTier(models.Model):
    TIER_CHOICES = [
        ('tier1', 'Tier 1'),
        ('tier2', 'Tier 2'),
        ('tier3', 'Tier 3'),
    ]
    
    country = models.CharField(max_length=100, unique=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    rate_per_click = models.DecimalField(max_digits=5, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} - {self.tier} (${self.rate_per_click}/click)"

    class Meta:
        ordering = ['country']
