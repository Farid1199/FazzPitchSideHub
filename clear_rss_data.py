"""
Database Reset Script - Clear Old RSS Data
This script removes all existing NewsItem and Opportunity records
so the improved scraper can fetch fresh, filtered content.
"""
from users.models import NewsItem, Opportunity

# Count existing items
news_count = NewsItem.objects.count()
opp_count = Opportunity.objects.count()

print(f"\n{'='*60}")
print("DATABASE RESET - Clearing Old RSS Data")
print(f"{'='*60}")
print(f"Current Database Status:")
print(f"  - News Items: {news_count}")
print(f"  - Opportunities: {opp_count}")
print(f"  - Total: {news_count + opp_count}")
print(f"{'='*60}\n")

# Confirm deletion
confirm = input("⚠️  This will DELETE all news items and opportunities. Continue? (yes/no): ")

if confirm.lower() == 'yes':
    print("\n🗑️  Deleting all NewsItems and Opportunities...")
    
    # Delete all opportunities (this also deletes the NewsItem base)
    deleted_opp = Opportunity.objects.all().delete()
    
    # Delete remaining news items (that weren't opportunities)
    deleted_news = NewsItem.objects.all().delete()
    
    print(f"✅ Deleted {deleted_opp[0]} opportunities")
    print(f"✅ Deleted {deleted_news[0]} news items")
    print(f"\n{'='*60}")
    print("✅ DATABASE CLEARED SUCCESSFULLY!")
    print(f"{'='*60}")
    print("\n📡 Next Steps:")
    print("   1. Exit the Django shell (type 'exit()')")
    print("   2. Run: python manage.py fetch_rss")
    print("   3. View the fresh data at http://127.0.0.1:8000/community-hub/")
    print(f"\n{'='*60}\n")
else:
    print("\n❌ Database reset cancelled. No changes made.\n")
