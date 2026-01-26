from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Acts as the base user for authentication with role-based access.
    """
    ROLE_CHOICES = [
        ('PLAYER', 'Player'),
        ('CLUB', 'Club'),
        ('SCOUT', 'Scout'),
        ('FAN', 'Fan'),
    ]

    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        blank=True,
        null=True,
        help_text="The role of the user in the system."
    )

    def __str__(self):
        return self.username


class PlayerProfile(models.Model):
    """
    Profile model for Players.
    Linked to User via OneToOneField.
    """
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('LB', 'Left Back'),
        ('CB', 'Centre Back'),
        ('RB', 'Right Back'),
        ('LWB', 'Left Wing Back'),
        ('RWB', 'Right Wing Back'),
        ('CDM', 'Defensive Midfielder'),
        ('CM', 'Central Midfielder'),
        ('CAM', 'Attacking Midfielder'),
        ('LM', 'Left Midfielder'),
        ('RM', 'Right Midfielder'),
        ('LW', 'Left Winger'),
        ('RW', 'Right Winger'),
        ('ST', 'Striker'),
        ('CF', 'Centre Forward'),
    ]
    
    PLAYING_LEVEL_CHOICES = [
        ('STEP_1', 'Step 1 (National League)'),
        ('STEP_2', 'Step 2 (National League North/South)'),
        ('STEP_3', 'Step 3 (Isthmian/Northern/Southern Premier)'),
        ('STEP_4', 'Step 4 (Isthmian/Northern/Southern Division One)'),
        ('STEP_5', 'Step 5 (Regional Leagues)'),
        ('STEP_6', 'Step 6 (County Leagues)'),
        ('STEP_7', 'Step 7 (Local Leagues)'),
        ('SUNDAY', 'Sunday League'),
        ('OTHER', 'Other'),
    ]
    
    PREFERRED_FOOT_CHOICES = [
        ('LEFT', 'Left'),
        ('RIGHT', 'Right'),
        ('BOTH', 'Both'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    position = models.CharField(
        max_length=3, 
        choices=POSITION_CHOICES, 
        help_text="Primary playing position.",
        default='ST'
    )
    location_postcode = models.CharField(
        max_length=10, 
        help_text="Postcode for player's location.",
        default=''
    )
    playing_level = models.CharField(
        max_length=10, 
        choices=PLAYING_LEVEL_CHOICES, 
        help_text="Current playing level (Step 1-7 or Sunday League).",
        default='SUNDAY'
    )
    height = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        help_text="Height in meters (e.g., 1.85).", 
        null=True, 
        blank=True
    )
    preferred_foot = models.CharField(
        max_length=5, 
        choices=PREFERRED_FOOT_CHOICES, 
        help_text="Preferred foot.",
        null=True,
        blank=True
    )
    youtube_highlight_url = models.URLField(
        max_length=500, 
        help_text="YouTube link to player highlights.", 
        blank=True
    )
    previous_clubs = models.TextField(
        blank=True, 
        help_text="List of previous clubs."
    )

    def __str__(self):
        return f"Player: {self.user.username}"


class ClubProfile(models.Model):
    """
    Profile model for Clubs.
    Can be linked to a User (for clubs that sign up) or standalone (for admin-added clubs).
    """
    LEAGUE_LEVEL_CHOICES = [
        ('STEP_1', 'Step 1 (National League)'),
        ('STEP_2', 'Step 2 (National League North/South)'),
        ('STEP_3', 'Step 3 (Isthmian/Northern/Southern Premier)'),
        ('STEP_4', 'Step 4 (Isthmian/Northern/Southern Division One)'),
        ('STEP_5', 'Step 5 (Regional Leagues)'),
        ('STEP_6', 'Step 6 (County Leagues)'),
        ('STEP_7', 'Step 7 (Local Leagues)'),
        ('SUNDAY', 'Sunday League'),
        ('OTHER', 'Other'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='club_profile',
        null=True,
        blank=True,
        help_text="Linked user account (only if club signed up). Leave blank for admin-added clubs."
    )
    club_name = models.CharField(
        max_length=100, 
        help_text="Official name of the club."
    )
    league_level = models.CharField(
        max_length=10, 
        choices=LEAGUE_LEVEL_CHOICES, 
        help_text="League level the club currently plays in.",
        default='SUNDAY'
    )
    location_postcode = models.CharField(
        max_length=10, 
        help_text="Postcode for club's location.",
        blank=True
    )
    rss_feed_url = models.URLField(
        max_length=500, 
        help_text="RSS feed URL for club news (for news scraper).", 
        blank=True
    )
    league = models.CharField(
        max_length=100, 
        help_text="League the club currently plays in.", 
        blank=True
    )
    location = models.CharField(
        max_length=100, 
        help_text="City or region of the club.", 
        blank=True
    )
    founded_year = models.PositiveIntegerField(
        help_text="Year the club was founded.", 
        null=True, 
        blank=True
    )
    is_registered = models.BooleanField(
        default=False,
        help_text="Whether this club has a registered user account."
    )

    def __str__(self):
        return f"Club: {self.club_name}"
    
    def save(self, *args, **kwargs):
        # Automatically set is_registered based on whether user exists
        self.is_registered = self.user is not None
        super().save(*args, **kwargs)


class ScoutProfile(models.Model):
    """
    Profile model for Scouts.
    Linked to User via OneToOneField.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scout_profile')
    organization = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Organization or Club the scout works for."
    )
    region = models.CharField(
        max_length=100, 
        help_text="Primary region covered by the scout.",
        default=''
    )

    def __str__(self):
        return f"Scout: {self.user.username}"


# Django Signals for automatic profile creation
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create the appropriate profile when a User is created
    based on their role.
    """
    if created and instance.role:
        if instance.role == 'PLAYER':
            PlayerProfile.objects.get_or_create(user=instance)
        elif instance.role == 'CLUB':
            ClubProfile.objects.get_or_create(user=instance)
        elif instance.role == 'SCOUT':
            ScoutProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile when the User is saved, if role has been assigned.
    """
    if instance.role:
        if instance.role == 'PLAYER' and hasattr(instance, 'player_profile'):
            instance.player_profile.save()
        elif instance.role == 'CLUB' and hasattr(instance, 'club_profile'):
            instance.club_profile.save()
        elif instance.role == 'SCOUT' and hasattr(instance, 'scout_profile'):
            instance.scout_profile.save()


class NewsItem(models.Model):
    """
    Model for storing news items fetched from club RSS feeds.
    """
    club = models.ForeignKey(
        ClubProfile, 
        on_delete=models.CASCADE, 
        related_name='news_items',
        help_text="The club this news item belongs to."
    )
    title = models.CharField(
        max_length=500, 
        help_text="Title of the news item."
    )
    link = models.URLField(
        max_length=1000, 
        help_text="Link to the full news article."
    )
    description = models.TextField(
        blank=True, 
        help_text="Description or summary of the news item."
    )
    published_date = models.DateTimeField(
        help_text="Date and time when the news was published."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this item was added to our database."
    )

    class Meta:
        ordering = ['-published_date']
        unique_together = ['club', 'link']  # Prevent duplicate entries

    def __str__(self):
        return f"{self.club.club_name}: {self.title}"


class Opportunity(NewsItem):
    """
    Model for trials and recruitment opportunities.
    Inherits from NewsItem and adds trial-specific fields.
    """
    target_position = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Target position(s) for the trial or recruitment (e.g., 'Striker', 'Midfielder')."
    )
    is_open = models.BooleanField(
        default=True,
        help_text="Whether the opportunity is still open for applications."
    )
    
    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return f"Opportunity: {self.title} ({self.club.club_name})"
