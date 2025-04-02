from django.contrib import admin
from .models import URL, URLAccess, DailyClickCount, PaymentRequest, CountryTier

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('original_url', 'short_code', 'user', 'created_at', 'click_count', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('original_url', 'short_code', 'user__username')
    readonly_fields = ('click_count',)

@admin.register(URLAccess)
class URLAccessAdmin(admin.ModelAdmin):
    list_display = ('url', 'accessed_at', 'ip_address', 'country', 'device_type', 'browser', 'os', 'earnings')
    list_filter = ('accessed_at', 'device_type', 'browser', 'os', 'country')
    search_fields = ('url__short_code', 'ip_address', 'country')
    readonly_fields = ('earnings',)

@admin.register(DailyClickCount)
class DailyClickCountAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'click_count')
    list_filter = ('date',)
    search_fields = ('user__username',)

@admin.register(CountryTier)
class CountryTierAdmin(admin.ModelAdmin):
    list_display = ('country', 'tier', 'rate_per_click', 'cpm_rate')
    list_filter = ('tier',)
    search_fields = ('country',)
    ordering = ('country',)
    readonly_fields = ('cpm_rate',)
    
    def cpm_rate(self, obj):
        # Calculate CPM (Cost Per Mille) rate
        cpm = float(obj.rate_per_click) * 1000
        return f"${cpm:.2f}/1000 clicks"
    cpm_rate.short_description = "CPM Rate"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('country', 'tier', 'rate_per_click', 'cpm_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('country',)
        return self.readonly_fields
