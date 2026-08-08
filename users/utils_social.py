import re
from django.contrib.auth import get_user_model
from .models import Hashtag, ProfileView

User = get_user_model()

def parse_post_content_for_tags_and_mentions(post):
    """
    Scans a post's caption for #hashtags and @mentions.
    Automatically creates hashtags and links mentions to the Post model.
    """
    if not post.caption:
        return

    # 1. Parse Hashtags (#)
    hashtags = re.findall(r'#(\w+)', post.caption)
    for tag_name in hashtags:
        tag_name_lower = tag_name.lower()
        hashtag_obj, created = Hashtag.objects.get_or_create(name=tag_name_lower)
        post.hashtags.add(hashtag_obj)

    # 2. Parse Mentions (@)
    mentions = re.findall(r'@(\w+)', post.caption)
    for username in mentions:
        try:
            user = User.objects.get(username__iexact=username)
            post.mentions.add(user)
        except User.DoesNotExist:
            pass

def track_profile_view(request, viewed_user):
    """
    Silently tracks a profile view footprint.
    Does not register if the user views their own profile.
    """
    if request.user.is_authenticated:
        if request.user != viewed_user:
            ProfileView.objects.create(
                viewed=viewed_user,
                viewer=request.user
            )
    else:
        # Anonymous view
        ProfileView.objects.create(
            viewed=viewed_user,
            viewer=None
        )
