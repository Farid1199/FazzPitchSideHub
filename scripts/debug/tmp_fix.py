import html
from django.utils.html import strip_tags
from users.models import NewsItem, Opportunity

count = 0
for item in NewsItem.objects.all():
    new_title = html.unescape(strip_tags(item.title))
    new_desc = html.unescape(strip_tags(item.description))
    if new_desc != item.description or new_title != item.title:
        item.title = new_title
        item.description = new_desc
        item.save()
        count += 1
        
print(f"Fixed {count} news items")
