import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='linkify_social')
def linkify_social(text):
    """
    Finds #hashtags and @mentions in text and turns them into clickable HTML links.
    """
    if not text:
        return text
        
    # Linkify @mentions (Points to the search page for that user)
    text = re.sub(
        r'@(\w+)',
        r'<a href="/search/?name=\1" class="text-blue-500 hover:text-blue-700 hover:underline font-medium">@\1</a>',
        text
    )
    
    # Linkify #hashtags (Points to the unified feed with a search query)
    text = re.sub(
        r'#(\w+)',
        r'<a href="/feeds/?q=%23\1" class="text-emerald-500 hover:text-emerald-700 hover:underline font-medium">#\1</a>',
        text
    )
    
    return mark_safe(text)