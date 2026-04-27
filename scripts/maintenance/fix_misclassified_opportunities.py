"""
Fix Misclassified Opportunities Script
Finds and downgrades incorrectly classified opportunities (like signings) to regular news items.
"""
from users.models import NewsItem, Opportunity

# Announcement keywords that should NOT be opportunities
announcement_keywords = [
    'signing', 'signed', 'signs', 'joins', 'joined', 'welcome',
    'captured', 'announces', 'announced', 'confirms', 'confirmed',
    'new signing', 'completes move', 'agrees deal'
]

print(f"\n{'='*70}")
print("FIX MISCLASSIFIED OPPORTUNITIES")
print(f"{'='*70}\n")

# Find misclassified opportunities
misclassified = []

for opp in Opportunity.objects.all():
    combined_text = (opp.title + ' ' + opp.description).lower()
    
    # Check if it contains announcement keywords
    has_announcement = any(keyword in combined_text for keyword in announcement_keywords)
    
    if has_announcement:
        misclassified.append(opp)
        print(f"❌ MISCLASSIFIED: {opp.title[:70]}")
        print(f"   ID: {opp.pk} | Published: {opp.published_date}")
        print(f"   Reason: Contains announcement keywords\n")

if not misclassified:
    print("✅ No misclassified opportunities found!\n")
    print(f"{'='*70}\n")
else:
    print(f"\n{'='*70}")
    print(f"Found {len(misclassified)} misclassified opportunities")
    print(f"{'='*70}\n")
    
    confirm = input("Delete these misclassified opportunities? (yes/no): ")
    
    if confirm.lower() == 'yes':
        count = 0
        for opp in misclassified:
            opp.delete()
            count += 1
        
        print(f"\n✅ Deleted {count} misclassified opportunities")
        print(f"{'='*70}\n")
    else:
        print("\n❌ Cleanup cancelled\n")
