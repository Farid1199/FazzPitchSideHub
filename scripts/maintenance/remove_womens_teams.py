"""
Remove women's teams and add appropriate men's teams for Birmingham
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubSource

# Remove women's teams
womens_teams = [
    'Birmingham City Women FC',
    'Aston Villa Women FC',
    'West Bromwich Albion Women FC'
]

print("Removing women's teams...")
for team_name in womens_teams:
    deleted_count = ClubSource.objects.filter(name=team_name).delete()[0]
    if deleted_count > 0:
        print(f"✅ Removed: {team_name}")

# Add proper men's teams
mens_teams = [
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
]

print("\nAdding men's teams...")
for team_data in mens_teams:
    club, created = ClubSource.objects.get_or_create(
        name=team_data['name'],
        defaults=team_data
    )
    if created:
        print(f"✅ Added: {club.name} ({club.get_league_level_display()})")
    else:
        print(f"⏭  Already exists: {club.name}")

print("\n" + "=" * 70)
print("Current ClubSource entries:")
print("-" * 70)
for source in ClubSource.objects.all().order_by('league_level', 'name'):
    rss_status = "✓ RSS" if source.rss_url else "✗ No RSS"
    print(f"  {source.name:<40} {source.get_league_level_display():<20} {rss_status}")
print("=" * 70)
