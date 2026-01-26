"""
Test script to demonstrate the fetch_rss command functionality.
Creates a test club with an RSS feed and runs the command.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, ClubProfile, NewsItem, Opportunity
from django.core.management import call_command

print("=" * 60)
print("Testing fetch_rss Management Command")
print("=" * 60)

# Check if we have any clubs with RSS feeds
clubs_with_rss = ClubProfile.objects.filter(rss_feed_url__isnull=False).exclude(rss_feed_url='')

if clubs_with_rss.exists():
    print(f"\nFound {clubs_with_rss.count()} club(s) with RSS feeds:")
    for club in clubs_with_rss:
        print(f"  - {club.club_name}: {club.rss_feed_url}")
    
    print("\n" + "=" * 60)
    print("Running fetch_rss command...")
    print("=" * 60 + "\n")
    
    call_command('fetch_rss')
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"Total NewsItems: {NewsItem.objects.count()}")
    print(f"Total Opportunities: {Opportunity.objects.count()}")
else:
    print("\n⚠ No clubs with RSS feeds found.")
    print("\nTo test this command, create a club with an RSS feed URL.")
    print("Example RSS feeds you can use for testing:")
    print("  - https://www.theguardian.com/football/rss")
    print("  - https://www.bbc.co.uk/sport/football/rss.xml")
    print("  - https://feeds.bbci.co.uk/sport/football/rss.xml")
    
print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
