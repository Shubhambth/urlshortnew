from django.core.management.base import BaseCommand
from shortener.models import CountryTier

class Command(BaseCommand):
    help = 'Populates the country tiers with initial data'

    def handle(self, *args, **kwargs):
        # Tier 1 countries (highest paying)
        tier1_countries = [
            ('United States', 0.05),
            ('Canada', 0.05),
            ('United Kingdom', 0.05),
            ('Australia', 0.05),
            ('Germany', 0.05),
            ('France', 0.05),
            ('Japan', 0.05),
            ('Switzerland', 0.05),
            ('Sweden', 0.05),
            ('Norway', 0.05),
        ]

        # Tier 2 countries (medium paying)
        tier2_countries = [
            ('Spain', 0.03),
            ('Italy', 0.03),
            ('Netherlands', 0.03),
            ('Belgium', 0.03),
            ('Austria', 0.03),
            ('Denmark', 0.03),
            ('Finland', 0.03),
            ('Ireland', 0.03),
            ('New Zealand', 0.03),
            ('Singapore', 0.03),
        ]

        # Tier 3 countries (lower paying)
        tier3_countries = [
            ('Brazil', 0.01),
            ('Mexico', 0.01),
            ('India', 0.10),
            ('China', 0.01),
            ('Russia', 0.01),
            ('South Africa', 0.01),
            ('Egypt', 0.01),
            ('Indonesia', 0.01),
            ('Philippines', 0.01),
            ('Vietnam', 0.01),
        ]

        # Create tier 1 countries
        for country, rate in tier1_countries:
            CountryTier.objects.get_or_create(
                country=country,
                defaults={'tier': 'tier1', 'rate_per_click': rate}
            )

        # Create tier 2 countries
        for country, rate in tier2_countries:
            CountryTier.objects.get_or_create(
                country=country,
                defaults={'tier': 'tier2', 'rate_per_click': rate}
            )

        # Create tier 3 countries
        for country, rate in tier3_countries:
            CountryTier.objects.get_or_create(
                country=country,
                defaults={'tier': 'tier3', 'rate_per_click': rate}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated country tiers')) 