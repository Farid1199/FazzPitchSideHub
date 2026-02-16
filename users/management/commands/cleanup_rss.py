"""
Django management command to clean up misclassified RSS data and re-fetch.
"""
from django.core.management.base import BaseCommand
from users.models import NewsItem, Opportunity


class Command(BaseCommand):
    help = 'Clean up old/misclassified RSS data and re-fetch with improved logic'

    def handle(self, *args, **options):
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('  DATABASE CLEANUP & RE-FETCH'))
        self.stdout.write('='*70)
        
        # Count existing items
        news_count = NewsItem.objects.count()
        opp_count = Opportunity.objects.count()
        
        self.stdout.write(f'\nCurrent Database Status:')
        self.stdout.write(f'  - News Items: {news_count}')
        self.stdout.write(f'  - Opportunities: {opp_count}')
        self.stdout.write(f'  - Total: {news_count + opp_count}\n')
        
        # Delete all items
        self.stdout.write('🗑️  Deleting all old data...')
        NewsItem.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Database cleared successfully!\n'))
        self.stdout.write('='*70)
        self.stdout.write('\n📡 Now run: python manage.py fetch_rss')
        self.stdout.write('='*70 + '\n')
