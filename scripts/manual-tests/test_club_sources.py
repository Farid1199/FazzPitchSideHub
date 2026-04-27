"""
Test script to demonstrate the new ClubSource functionality.
This creates sample ClubSource entries for Birmingham clubs.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubSource, NewsItem, Opportunity

def create_sample_club_sources():
    """Create sample ClubSource entries for testing"""
    
    sample_clubs = [
        {
            'name': 'Birmingham City FC',
            'league_level': 'L3',
            'website_url': 'https://www.bcfc.com/',
            'rss_url': 'https://www.bcfc.com/feed/',
            'logo_url': '',
            'region': 'Birmingham'
        },
        {
            'name': 'Aston Villa FC',
            'league_level': 'L1',
            'website_url': 'https://www.avfc.co.uk/',
            'rss_url': 'https://www.avfc.co.uk/feed/',
            'logo_url': '',
            'region': 'Birmingham'
        },
        {
            'name': 'West Bromwich Albion FC',
            'league_level': 'L2',
            'website_url': 'https://www.wba.co.uk/',
            'rss_url': 'https://www.wba.co.uk/feed/',
            'logo_url': '',
            'region': 'Birmingham'
        },
        {
            'name': 'Solihull Moors FC',
            'league_level': 'L6',
            'website_url': 'https://www.solihullmoorsfc.co.uk/',
            'rss_url': 'https://www.solihullmoorsfc.co.uk/feed/',
            'logo_url': '',
            'region': 'Birmingham'
        },
        {
            'name': 'Sutton Coldfield Town FC',
            'league_level': 'L10',
            'website_url': 'https://www.suttoncfc.com/',
            'rss_url': '',
            'logo_url': '',
            'region': 'Birmingham'
        },
    ]
    
    print("=" * 70)
    print("Creating Sample ClubSource Entries for Birmingham")
    print("=" * 70)
    
    created_count = 0
    skipped_count = 0
    
    for club_data in sample_clubs:
        club_name = club_data['name']
        
        # Check if already exists
        if ClubSource.objects.filter(name=club_name).exists():
            print(f"⏭  Skipped: {club_name} (already exists)")
            skipped_count += 1
            continue
        
        # Create the ClubSource
        club_source = ClubSource.objects.create(**club_data)
        print(f"✅ Created: {club_source.name} ({club_source.get_league_level_display()})")
        
        if club_source.rss_url:
            print(f"   📡 RSS Feed: {club_source.rss_url}")
        else:
            print(f"   ⚠  No RSS feed configured")
        
        created_count += 1
    
    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  ✅ Created: {created_count}")
    print(f"  ⏭  Skipped: {skipped_count}")
    print(f"  📊 Total ClubSource entries: {ClubSource.objects.count()}")
    print("=" * 70)
    
    # Display all ClubSource entries
    print("\nAll ClubSource entries in database:")
    print("-" * 70)
    for source in ClubSource.objects.all().order_by('league_level', 'name'):
        rss_status = "✓ RSS" if source.rss_url else "✗ No RSS"
        print(f"  {source.name:<40} {source.get_league_level_display():<20} {rss_status}")
    print("-" * 70)
    
    # Show news/opportunity counts
    total_news = NewsItem.objects.filter(source__isnull=False).count()
    total_opps = Opportunity.objects.filter(source__isnull=False).count()
    
    print(f"\nCurrent Content Statistics:")
    print(f"  📰 News Items from RSS sources: {total_news}")
    print(f"  🎯 Opportunities from RSS sources: {total_opps}")
    print(f"\nTo fetch RSS content, run:")
    print(f"  python manage.py fetch_rss")
    print("=" * 70)

if __name__ == '__main__':
    create_sample_club_sources()
