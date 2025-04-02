from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shortener.models import URL, URLAccess, DailyClickCount, PaymentRequest, CountryTier

class Command(BaseCommand):
    help = 'Clears all data from the database to start fresh'

    def handle(self, *args, **kwargs):
        # Delete all data from shortener models
        URLAccess.objects.all().delete()
        DailyClickCount.objects.all().delete()
        PaymentRequest.objects.all().delete()
        URL.objects.all().delete()
        
        # Delete all users except superuser
        User.objects.filter(is_superuser=False).delete()
        
        # Reset country tiers
        CountryTier.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared all data'))
        self.stdout.write(self.style.SUCCESS('You can now run populate_country_tiers to set up country tiers')) 