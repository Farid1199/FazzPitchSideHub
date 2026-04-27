"""
Test script to verify the homepage setup is working correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubProfile, NewsItem, Opportunity


def main():
    print("=" * 70)
    print("HOMEPAGE SETUP VERIFICATION")
    print("=" * 70)

    # Check for clubs
    clubs = ClubProfile.objects.all()
    print(f"\nTotal Clubs: {clubs.count()}")

    # Check for news items
    news = NewsItem.objects.all()
    print(f"Total News Items: {news.count()}")

    # Check for opportunities
    opportunities = Opportunity.objects.all()
    print(f"Total Opportunities: {opportunities.count()}")

    print("\n" + "-" * 70)
    print("HOMEPAGE DATA PREVIEW:")
    print("-" * 70)

    # Show what would appear on homepage
    latest_news = NewsItem.objects.all()[:5]
    latest_opportunities = Opportunity.objects.filter(is_open=True)[:5]

    print("\nLatest News (up to 5):")
    if latest_news:
        for i, item in enumerate(latest_news, 1):
            club_name = item.club.club_name if item.club else "Unknown club"
            print(f"  {i}. {item.title[:60]}...")
            print(f"     Club: {club_name}")
    else:
        print("  No news items yet.")

    print("\nLatest Opportunities (up to 5):")
    if latest_opportunities:
        for i, opp in enumerate(latest_opportunities, 1):
            club_name = opp.club.club_name if opp.club else "Unknown club"
            print(f"  {i}. {opp.title[:60]}...")
            print(f"     Club: {club_name}")
            if opp.target_position:
                print(f"     Position: {opp.target_position}")
    else:
        print("  No opportunities yet.")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("\n1. Start the development server:")
    print("   python manage.py runserver")
    print("\n2. Visit the homepage:")
    print("   http://localhost:8000/")
    print("\n3. If no news/opportunities show up, add some clubs and run:")
    print("   python manage.py fetch_rss")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
