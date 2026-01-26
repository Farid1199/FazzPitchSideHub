"""
Bulk add multiple clubs from a list.
These are admin-added clubs (no user accounts) for RSS feed tracking.
Edit the CLUBS list below with your specific clubs and their RSS feeds.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubProfile

# EDIT THIS LIST WITH YOUR CLUBS
# Format: (club_name, rss_feed_url, league_level, postcode, location)
CLUBS = [
    # Example entries - replace with your actual clubs:
    # ("Dulwich Hamlet", "https://www.dulwichhamletfc.co.uk/feed/", "STEP_3", "SE22 8BD", "London"),
    # ("Hashtag United", "https://hashtagunited.co.uk/feed/", "STEP_5", "CM24 8GU", "Essex"),
    # ("Billericay Town", "https://www.billericaytownfc.co.uk/feed/", "STEP_3", "CM12 9PZ", "Essex"),
    
    # Add your clubs here:
    
]

def add_clubs():
    """Add all clubs from the CLUBS list (without user accounts)"""
    print("=" * 60)
    print("Bulk Adding Clubs (Admin-Added, No User Accounts)")
    print("=" * 60)
    
    if not CLUBS:
        print("\n⚠ No clubs defined in the CLUBS list.")
        print("Edit this file and add your clubs to the CLUBS list at the top.")
        return
    
    added = 0
    skipped = 0
    errors = 0
    
    for club_data in CLUBS:
        club_name = club_data[0]
        rss_url = club_data[1]
        league_level = club_data[2] if len(club_data) > 2 else 'SUNDAY'
        postcode = club_data[3] if len(club_data) > 3 else ''
        location = club_data[4] if len(club_data) > 4 else ''
        
        print(f"\nProcessing: {club_name}")
        
        # Check if exists
        if ClubProfile.objects.filter(club_name=club_name).exists():
            print(f"  ⚠ Skipped - already exists")
            skipped += 1
            continue
        
        try:
            # Create club profile WITHOUT user account
            club_profile = ClubProfile.objects.create(
                club_name=club_name,
                rss_feed_url=rss_url,
                league_level=league_level,
                location_postcode=postcode,
                location=location,
                user=None,  # No user account
                is_registered=False
            )
            
            print(f"  ✓ Added successfully")
            print(f"    RSS: {rss_url}")
            print(f"    League: {league_level}")
            added += 1
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            errors += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Added: {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 60)
    
    if added > 0:
        print("\nNow run: python manage.py fetch_rss")
        print("To fetch news from all clubs with RSS feeds")
        print("\nNote: These clubs are admin-added and don't have user accounts.")
        print("Clubs can still sign up separately and create their own accounts.")

if __name__ == '__main__':
    add_clubs()
