"""
Demo: Two Types of Clubs in the System

1. Admin-Added Clubs: Clubs you add for RSS tracking (no user accounts)
2. Registered Clubs: Clubs that sign up themselves (have user accounts)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, ClubProfile

print("=" * 70)
print("FAZZ PITCHSIDE HUB - TWO TYPES OF CLUBS")
print("=" * 70)

print("\n📋 TYPE 1: ADMIN-ADDED CLUBS (for RSS tracking)")
print("-" * 70)
print("These are clubs YOU add as admin to track their RSS feeds.")
print("They don't have user accounts and can't log in.")
print("\nExample:")
print("  Club Name: Dulwich Hamlet FC")
print("  RSS Feed: https://www.dulwichhamletfc.co.uk/feed/")
print("  Has User Account: NO")
print("  Can Login: NO")
print("  Purpose: Auto-fetch news/opportunities from RSS")

print("\n\n👥 TYPE 2: REGISTERED CLUBS (actual users)")
print("-" * 70)
print("These are clubs that SIGN UP to your platform.")
print("They create accounts, login, and manage their own profiles.")
print("\nExample:")
print("  Club Name: Arsenal FC")
print("  Username: arsenal_fc")
print("  Has User Account: YES")
print("  Can Login: YES")
print("  Purpose: Post opportunities, manage profile, interact with players")

print("\n\n" + "=" * 70)
print("CURRENT CLUBS IN DATABASE:")
print("=" * 70)

all_clubs = ClubProfile.objects.all()

if all_clubs.exists():
    admin_clubs = all_clubs.filter(user__isnull=True)
    registered_clubs = all_clubs.filter(user__isnull=False)
    
    print(f"\n📋 Admin-Added Clubs: {admin_clubs.count()}")
    for club in admin_clubs:
        print(f"  - {club.club_name} (RSS: {club.rss_feed_url or 'None'})")
    
    print(f"\n👥 Registered Clubs: {registered_clubs.count()}")
    for club in registered_clubs:
        print(f"  - {club.club_name} (User: {club.user.username})")
else:
    print("\nNo clubs in database yet.")

print("\n\n" + "=" * 70)
print("HOW TO ADD CLUBS:")
print("=" * 70)

print("\n1️⃣ Add clubs for RSS tracking (no user account):")
print('   python manage.py add_club "Club Name" "https://club.com/feed"')
print("   OR edit and run: python bulk_add_clubs.py")
print("   OR use Django Admin interface")

print("\n2️⃣ Clubs sign up themselves (creates user account):")
print("   They register through your website signup form")
print("   This happens when your platform goes live")

print("\n\n" + "=" * 70)
print("BENEFITS OF THIS APPROACH:")
print("=" * 70)
print("✓ You can track ANY club's RSS feed (even if they don't sign up)")
print("✓ Clubs can still sign up and get full platform access")
print("✓ No conflict between admin-added and registered clubs")
print("✓ The 'is_registered' field tracks which is which")
print("=" * 70)
