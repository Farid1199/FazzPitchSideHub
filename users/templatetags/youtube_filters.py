from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='youtube_embed_url')
def youtube_embed_url(url):
    """
    Convert a YouTube URL to an embed URL.
    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    if not url:
        return ''
    
    # Pattern to extract video ID from various YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
    
    # If already an embed URL, return as is
    if 'youtube.com/embed/' in url:
        return url
    
    return ''


@register.filter(name='embed_youtube_video')
def embed_youtube_video(url):
    """
    Convert a YouTube URL to an embedded iframe.
    Returns the full HTML iframe tag ready to be displayed.
    """
    if not url:
        return ''
    
    # Get the embed URL using the existing filter
    embed_url = youtube_embed_url(url)
    
    if not embed_url:
        return ''
    
    # Create the iframe HTML
    iframe_html = f'''<iframe 
        width="100%" 
        height="100%" 
        src="{embed_url}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
        class="w-full h-full">
    </iframe>'''
    
    return mark_safe(iframe_html)
