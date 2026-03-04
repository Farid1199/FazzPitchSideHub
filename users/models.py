from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Acts as the base user for authentication with role-based access.
    """
    ROLE_CHOICES = [
        ('PLAYER', 'Player'),
        ('CLUB', 'Club'),
        ('SCOUT', 'Scout'),
        ('MANAGER', 'Manager'),
        ('FAN', 'Fan'),
    ]

    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        blank=True,
        null=True,
        help_text="The role of the user in the system."
    )
    is_private = models.BooleanField(
        default=False,
        help_text="If True, only approved followers can see full profile."
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
    video_file = models.FileField(
        upload_to='player_videos/',
        blank=True,
        null=True,
        help_text="Upload a highlight video (MP4, AVI, MOV). Max size: 50MB."
    )
    previous_clubs = models.TextField(
        blank=True, 
        help_text="List of previous clubs."
    )
    current_team = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current team/club name."
    )
    available_for_club = models.BooleanField(
        default=False,
        help_text="Whether the player is looking for a club."
    )

    AVAILABILITY_CHOICES = [
        ('AVAILABLE', 'Available — Actively Looking'),
        ('OPEN', 'Open to Offers'),
        ('CONTRACTED', 'Contracted — Not Available'),
        ('TRIALLING', 'Currently on Trial'),
        ('INJURED', 'Unavailable — Injured'),
    ]
    availability_status = models.CharField(
        max_length=15,
        choices=AVAILABILITY_CHOICES,
        default='AVAILABLE',
        help_text="Current availability status."
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text='A short professional bio shown on your profile'
    )

    def __str__(self):
        return f"Player: {self.user.username}"


class ClubSource(models.Model):
    """
    Independent model for RSS feed sources (Admin-managed only).
    This is NOT linked to user accounts - used purely for aggregating news.
    Admin can add any club here to scrape their RSS feeds.
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
    
    name = models.CharField(
        max_length=100,
        help_text="Official name of the club (e.g., 'Halesowen Town FC').",
        unique=True
    )
    league_level = models.CharField(
        max_length=10,
        choices=LEAGUE_LEVEL_CHOICES,
        help_text="League level the club plays in.",
        default='SUNDAY'
    )
    website_url = models.URLField(
        max_length=500,
        help_text="Official club website URL.",
        blank=True
    )
    rss_url = models.URLField(
        max_length=500,
        help_text="RSS feed URL for automatic news scraping.",
        blank=True
    )
    logo_url = models.URLField(
        max_length=500,
        help_text="URL to the club's logo image.",
        blank=True
    )
    region = models.CharField(
        max_length=100,
        help_text="Region/city (e.g., 'Birmingham', 'West Midlands').",
        default='Birmingham'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['league_level', 'name']
        verbose_name = 'Club Source (RSS)'
        verbose_name_plural = 'Club Sources (RSS)'
    
    def __str__(self):
        return f"{self.name} ({self.get_league_level_display()})"


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
    website_url = models.URLField(
        max_length=500,
        help_text="Official club website URL.",
        blank=True
    )
    rss_feed_url = models.URLField(
        max_length=500, 
        help_text="RSS feed URL for club news (for news scraper).", 
        blank=True
    )
    logo_url = models.URLField(
        max_length=500,
        help_text="URL to the club's logo image.",
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
    TIER_CHOICES = [
        ('TIER1', 'FAZZ Verified Scout'),
        ('TIER2', 'FAZZ Advanced Verified'),
        ('TIER3', 'FAZZ Professional Verified'),
    ]

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
    scout_verified = models.BooleanField(
        default=False,
        help_text="Whether this scout has been verified by the platform."
    )
    verification_tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        blank=True,
        null=True,
        help_text="Verified tier awarded by admin."
    )

    def __str__(self):
        return f"Scout: {self.user.username}"


class ManagerProfile(models.Model):
    """
    Profile model for Managers/Coaches.
    Linked to User via OneToOneField.
    """
    QUALIFICATION_CHOICES = [
        ('NONE', 'No Formal Qualification'),
        ('INTRO', 'Introduction to Coaching Football (Level 1)'),
        ('UEFA_C', 'UEFA C Licence (Level 2)'),
        ('UEFA_B', 'UEFA B Licence (Level 3)'),
        ('UEFA_A', 'UEFA A Licence (Level 4)'),
        ('UEFA_PRO', 'UEFA Pro Licence (Level 5)'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('EMPLOYED', 'Currently Employed'),
        ('OPEN', 'Open to Offers'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    
    # Basic Info
    club_name = models.CharField(
        max_length=100,
        help_text="Name of the club currently managing.",
        blank=True
    )
    current_role = models.CharField(
        max_length=100,
        help_text="e.g., First Team Manager, Assistant Manager, U23 Coach.",
        blank=True
    )
    location_postcode = models.CharField(
        max_length=10,
        help_text="Postcode for manager's location.",
        blank=True
    )
    
    # Professional Details
    coaching_philosophy = models.TextField(
        blank=True,
        help_text="Describe your coaching style and philosophy (e.g., 'High pressing', 'Possession-based')."
    )
    preferred_formation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Preferred tactical formation (e.g., 4-4-2, 4-3-3)."
    )
    years_of_experience = models.PositiveIntegerField(
        help_text="Years of managerial experience.",
        null=True,
        blank=True
    )
    
    # Career History
    career_history = models.TextField(
        blank=True,
        help_text="List previous clubs, roles, and dates (e.g., '2020-2022: First Team Manager at FC United')."
    )
    achievements = models.TextField(
        blank=True,
        help_text="List trophies, titles, and notable achievements (e.g., 'Isthmian League North Winner 2022')."
    )
    
    # Statistics
    games_managed = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of games managed."
    )
    win_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Win percentage (e.g., 65.50 for 65.5%)."
    )
    
    # Qualifications
    highest_qualification = models.CharField(
        max_length=20,
        choices=QUALIFICATION_CHOICES,
        default='NONE',
        help_text="Highest coaching qualification held."
    )
    additional_badges = models.TextField(
        blank=True,
        help_text="Additional qualifications (e.g., 'FA Youth Award', 'Goalkeeping Level 2')."
    )
    qualification_verified = models.BooleanField(
        default=False,
        help_text="Whether the coaching qualification has been verified by admin."
    )
    
    # Availability
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='EMPLOYED',
        help_text="Current employment status."
    )

    def __str__(self):
        return f"Manager: {self.user.username}"
    
    def get_win_percentage(self):
        """Calculate and return win percentage if stats are available."""
        if self.games_managed and self.win_rate:
            return f"{self.win_rate}%"
        return "N/A"


class QualificationVerification(models.Model):
    """
    Model to store uploaded coaching certificates for Fazz Pitchside verification.
    Managers must provide: certificate, FA dashboard screenshot, and FAN number.
    Verification is performed manually by platform administrators.
    
    IMPORTANT: This is a Fazz Pitchside platform-level verification.
    It is NOT an official endorsement by The Football Association.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Fazz Pitchside Verified'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged for Further Review'),
    ]
    
    manager = models.ForeignKey(
        ManagerProfile, 
        on_delete=models.CASCADE, 
        related_name='verification_requests'
    )
    qualification_type = models.CharField(
        max_length=20,
        choices=ManagerProfile.QUALIFICATION_CHOICES,
        help_text="Type of qualification being verified."
    )
    certificate_image = models.FileField(
        upload_to='coaching_certificates/',
        help_text="Upload a clear photo, scan, or PDF of your coaching certificate. "
                  "Your full name and qualification level must be visible."
    )
    dashboard_screenshot = models.ImageField(
        upload_to='coaching_dashboard_screenshots/',
        help_text="Upload a screenshot from your England Football Learning dashboard showing "
                  "your name, FAN number, and licence level. This is required for cross-verification.",
        blank=True,
        null=False,
        default=''
    )
    fa_fan_number = models.CharField(
        max_length=50,
        help_text="Your FA FAN (Football Affiliate Number). This is required for cross-reference "
                  "against your dashboard screenshot.",
        default=''
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_licences',
        help_text="The admin who reviewed this verification request."
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal admin notes on the verification decision. NOT visible to the user."
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection. This IS visible to the manager so they can resubmit."
    )
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Coaching Licence Verification'
        verbose_name_plural = 'Coaching Licence Verifications'
    
    def __str__(self):
        return f"{self.manager.user.username} - {self.get_qualification_type_display()} ({self.get_status_display()})"


class ScoutVerification(models.Model):
    """
    Tiered Scout Verification System.
    Scouts submit evidence documents; admins manually review and award a tier badge.

    TIER 1 — FAZZ Verified Scout       (Basic / Grassroots)
    TIER 2 — FAZZ Advanced Verified    (Semi-Pro)
    TIER 3 — FAZZ Professional Verified (Professional / Club-Attached)

    IMPORTANT: This is a Fazz Pitchside platform-level verification.
    It is NOT an official endorsement by The Football Association or any governing body.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged for Further Review'),
    ]

    TIER_CHOICES = [
        ('TIER1', 'FAZZ Verified Scout'),
        ('TIER2', 'FAZZ Advanced Verified'),
        ('TIER3', 'FAZZ Professional Verified'),
    ]

    QUALIFICATION_BODY_CHOICES = [
        ('FA', 'The Football Association (FA)'),
        ('PFSA', 'Professional Football Scouts Association (PFSA)'),
        ('OTHER', 'Other Recognised Course'),
        ('NONE', 'No Formal Qualification'),
    ]

    QUALIFICATION_LEVEL_CHOICES = [
        ('FA_L1', 'FA Level 1 – Introduction to Talent ID'),
        ('FA_L2', 'FA Level 2 – National Talent ID & Scouting'),
        ('FA_L3', 'FA Level 3 – Advanced Principles of Talent ID'),
        ('FA_L4', 'FA Level 4 – Leadership of Talent ID'),
        ('FA_L5', 'FA Level 5 – Technical Directors Course'),
        ('PFSA_L1', 'PFSA Level 1 – Talent ID'),
        ('PFSA_L2', 'PFSA Level 2 – Talent ID'),
        ('PFSA_L3', 'PFSA Level 3 – Talent ID'),
        ('PFSA_OPP', 'PFSA Opposition Analysis'),
        ('PFSA_TECH', 'PFSA Technical Scouting'),
        ('OTHER', 'Other Recognised Course'),
        ('NONE', 'No Formal Qualification'),
    ]

    scout = models.OneToOneField(
        ScoutProfile,
        on_delete=models.CASCADE,
        related_name='verification'
    )

    qualification_body = models.CharField(
        max_length=10,
        choices=QUALIFICATION_BODY_CHOICES,
        help_text="Awarding body for the qualification."
    )
    qualification_level = models.CharField(
        max_length=20,
        choices=QUALIFICATION_LEVEL_CHOICES,
        help_text="Level of qualification being verified."
    )

    fa_fan_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="FA FAN number (required for FA qualifications)."
    )

    certificate_file = models.FileField(
        upload_to='scout_certificates/',
        help_text="Upload your qualification certificate (PDF or image)."
    )
    dashboard_screenshot = models.ImageField(
        upload_to='scout_dashboards/',
        blank=True,
        null=True,
        help_text="England Football dashboard screenshot (FA route only)."
    )
    safeguarding_certificate = models.FileField(
        upload_to='scout_safeguarding/',
        blank=True,
        null=True,
        help_text="Safeguarding certificate (required for Tier 2+)."
    )
    dbs_expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text="DBS certificate expiry date (required for Tier 2+)."
    )
    club_affiliation_proof = models.FileField(
        upload_to='scout_club_proof/',
        blank=True,
        null=True,
        help_text="Signed club letter or official club email (Tier 3)."
    )
    sample_scout_report = models.FileField(
        upload_to='scout_reports/',
        blank=True,
        null=True,
        help_text="Sample anonymised scout report (Tier 3)."
    )

    requested_tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        default='TIER1',
        help_text="Tier the scout is applying for."
    )
    awarded_tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        blank=True,
        null=True,
        help_text="Tier actually awarded by admin (may differ from requested)."
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scout_verifications_reviewed',
        help_text="The admin who reviewed this verification request."
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal admin notes (not visible to scout)."
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason shown to scout on rejection."
    )

    class Meta:
        verbose_name = 'Scout Verification'
        verbose_name_plural = 'Scout Verifications'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.scout} – {self.get_status_display()} ({self.get_requested_tier_display()})"


class Notification(models.Model):
    """
    In-app notification for users.
    Created for verification, follows, likes, messages, opportunities, etc.
    """
    TYPE_CHOICES = [
        ('verification', 'Verification Update'),
        ('follow', 'New Follower'),
        ('follow_request', 'Follow Request'),
        ('follow_accepted', 'Follow Request Accepted'),
        ('like', 'Post Liked'),
        ('message', 'New Message'),
        ('opportunity', 'New Opportunity'),
        ('system', 'System Notification'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='system'
    )
    action_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"
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
        elif instance.role == 'MANAGER':
            ManagerProfile.objects.get_or_create(user=instance)
        elif instance.role == 'FAN':
            FanProfile.objects.get_or_create(user=instance)


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
        elif instance.role == 'MANAGER' and hasattr(instance, 'manager_profile'):
            instance.manager_profile.save()
        elif instance.role == 'FAN' and hasattr(instance, 'fan_profile'):
            instance.fan_profile.save()


class NewsItem(models.Model):
    """
    Model for storing news items.
    Can be sourced from:
    1. RSS feeds (links to ClubSource) - Admin-managed
    2. Manual posts (links to ClubProfile) - User-managed (future)
    """
    CATEGORY_CHOICES = [
        ('trial', 'Trial News'),
        ('general', 'General News'),
        ('transfer', 'Transfer News'),
        ('match', 'Match Reports'),
    ]

    # RSS Source (Admin-managed aggregation)
    source = models.ForeignKey(
        ClubSource,
        on_delete=models.CASCADE,
        related_name='news_items',
        null=True,
        blank=True,
        help_text="The RSS club source (for aggregated content)."
    )
    
    # User Source (Manual posts by registered clubs)
    club = models.ForeignKey(
        ClubProfile, 
        on_delete=models.CASCADE, 
        related_name='news_items',
        null=True,
        blank=True,
        help_text="The registered club (for user-posted content)."
    )
    
    title = models.CharField(
        max_length=500, 
        help_text="Title of the news item."
    )
    link = models.URLField(
        max_length=1000, 
        help_text="Link to the full news article.",
        unique=True  # Prevent duplicates across all sources
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
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of the news item."
    )

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        if self.source:
            return f"{self.source.name}: {self.title}"
        elif self.club:
            return f"{self.club.club_name}: {self.title}"
        return self.title
    
    def get_club_name(self):
        """Helper to get club name from either source"""
        return self.source.name if self.source else (self.club.club_name if self.club else "Unknown")
    
    def get_league_display(self):
        """Helper to get league level display"""
        if self.source:
            return self.source.get_league_level_display()
        elif self.club:
            return self.club.get_league_level_display()
        return "Unknown"


class Opportunity(NewsItem):
    """
    Model for trials and recruitment opportunities.
    Inherits from NewsItem and adds trial-specific fields.
    Can be sourced from RSS feeds (ClubSource) or manual posts (ClubProfile).
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
    is_verified = models.BooleanField(
        default=False, 
        help_text="Verified by an official club manager"
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_opportunities',
        help_text="User who verified this opportunity."
    )
    CONTRACT_TYPE_CHOICES = [
        ('AMATEUR', 'Amateur'),
        ('SEMI_PRO', 'Semi-Professional'),
        ('EXPENSES', 'Expenses Only'),
        ('PAID', 'Paid'),
        ('UNSPECIFIED', 'Not Specified'),
    ]
    contract_type = models.CharField(
        max_length=15,
        choices=CONTRACT_TYPE_CHOICES,
        default='UNSPECIFIED'
    )
    age_min = models.PositiveIntegerField(null=True, blank=True)
    age_max = models.PositiveIntegerField(null=True, blank=True)
    trial_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    positions_needed = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma-separated list of positions needed'
    )
    level_required = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g. Step 3-4, Sunday League, County League'
    )
    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = "Opportunities"

    def __str__(self):
        club_name = self.get_club_name()
        return f"Opportunity: {self.title} ({club_name})"


class Post(models.Model):
    """
    Social media-style post model for Players, Managers, and Scouts.
    Allows users to share achievements, highlights, match reports, and general updates.
    """
    POST_TYPE_CHOICES = [
        ('GENERAL', 'General Update'),
        ('ACHIEVEMENT', 'Achievement'),
        ('MATCH_REPORT', 'Match Report'),
        ('TRAINING', 'Training Session'),
        ('HIGHLIGHT', 'Highlight Video'),
        ('MILESTONE', 'Career Milestone'),
        ('TRANSFER', 'Transfer News'),
        ('AWARD', 'Award/Recognition'),
        # Manager-specific
        ('TACTICAL', 'Tactical Analysis'),
        ('COACHING', 'Coaching Insights'),
        ('TEAM_NEWS', 'Team News'),
        # Scout-specific
        ('PLAYER_REPORT', 'Player Scouting Report'),
        ('TALENT_SPOT', 'Talent Spotting'),
    ]
    
    # Core Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='GENERAL',
        help_text="Type of post (achievement, match report, etc.)"
    )
    caption = models.TextField(
        help_text="Post caption/description",
        max_length=1000
    )
    
    # Media Fields
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        help_text="Upload an image for the post"
    )
    video = models.FileField(
        upload_to='post_videos/',
        blank=True,
        null=True,
        help_text="Upload a video (MP4, AVI, MOV). Max size: 100MB"
    )
    youtube_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="YouTube video link"
    )
    
    # Achievement Fields (for players)
    goals = models.IntegerField(
        null=True,
        blank=True,
        help_text="Goals scored"
    )
    assists = models.IntegerField(
        null=True,
        blank=True,
        help_text="Assists provided"
    )
    clean_sheets = models.IntegerField(
        null=True,
        blank=True,
        help_text="Clean sheets (for goalkeepers)"
    )
    minutes_played = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes played in the match"
    )
    match_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Match rating (e.g., 8.5)"
    )
    
    # Match Details
    match_opponent = models.CharField(
        max_length=100,
        blank=True,
        help_text="Opponent team name"
    )
    match_result = models.CharField(
        max_length=20,
        blank=True,
        help_text="Match result (e.g., 'Won 3-1', 'Drew 2-2')"
    )
    match_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the match"
    )
    competition = models.CharField(
        max_length=100,
        blank=True,
        help_text="Competition name (e.g., 'FA Cup', 'League Cup')"
    )
    
    # Award/Milestone Fields
    award_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Award or milestone title"
    )
    award_description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Award or milestone description"
    )
    
    # Manager-Specific Fields
    tactical_analysis = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Tactical analysis or coaching insights (for managers)"
    )
    team_formation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Formation used (e.g., 4-3-3, 3-5-2)"
    )
    team_performance = models.TextField(
        max_length=500,
        blank=True,
        help_text="Team performance summary"
    )
    coaching_methodology = models.TextField(
        max_length=500,
        blank=True,
        help_text="Coaching methodology or training approach"
    )
    
    # Scout-Specific Fields
    player_scouted = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of player scouted"
    )
    player_position = models.CharField(
        max_length=20,
        blank=True,
        help_text="Position of scouted player"
    )
    player_age = models.IntegerField(
        null=True,
        blank=True,
        help_text="Age of scouted player"
    )
    player_club = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current club of scouted player"
    )
    scouting_report = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Detailed scouting report or assessment"
    )
    strengths = models.TextField(
        max_length=500,
        blank=True,
        help_text="Player's key strengths"
    )
    areas_for_improvement = models.TextField(
        max_length=500,
        blank=True,
        help_text="Areas where player can improve"
    )
    potential_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Potential rating (out of 10)"
    )
    
    # Engagement
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        blank=True,
        help_text="Users who liked this post"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_post_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def total_likes(self):
        return self.likes.count()
    
    def get_user_role(self):
        """Get the role of the user who created the post"""
        return self.user.get_role_display() if self.user.role else "User"
    
    def get_profile_info(self):
        """Get profile information based on user role"""
        if self.user.role == 'PLAYER' and hasattr(self.user, 'player_profile'):
            return {
                'position': self.user.player_profile.get_position_display(),
                'team': self.user.player_profile.current_team or 'Free Agent',
                'level': self.user.player_profile.get_playing_level_display()
            }
        elif self.user.role == 'MANAGER' and hasattr(self.user, 'manager_profile'):
            return {
                'role': self.user.manager_profile.current_role or 'Manager',
                'club': self.user.manager_profile.club_name or 'Unattached',
                'qualification': self.user.manager_profile.get_highest_qualification_display() if hasattr(self.user.manager_profile, 'highest_qualification') else 'N/A'
            }
        elif self.user.role == 'SCOUT' and hasattr(self.user, 'scout_profile'):
            return {
                'organization': self.user.scout_profile.organization or 'Independent Scout',
                'region': self.user.scout_profile.region or 'N/A'
            }
        return {}

    def total_comments(self):
        return self.comments.count()


# ===================================================================
# Post Comments
# ===================================================================

class Comment(models.Model):
    """Comment on a social post."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.post.pk}: {self.body[:40]}"


class TrialView(models.Model):
    """
    Tracks when a player views a trial opportunity detail page.
    Used for behavioral boosting in the recommendation engine:
    - Viewing a trial signals interest (+2 score boost)
    - Data collected here supports future deep learning models
    """
    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name='trial_views'
    )
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='player_views'
    )
    viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of times this player viewed this trial."
    )

    class Meta:
        unique_together = ('player', 'opportunity')
        ordering = ['-viewed_at']
        verbose_name = "Trial View"
        verbose_name_plural = "Trial Views"

    def __str__(self):
        return f"{self.player.user.username} viewed {self.opportunity.title}"


class TrialApplication(models.Model):
    """
    Tracks when a player expresses interest in a trial opportunity.
    Used in the recommendation engine for:
    - Collaborative filtering: find trials that similar players applied to (+6 boost)
    - Suppression: don't re-recommend trials the player already applied to (-100)
    - Data collected here supports future deep learning models
    """
    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name='trial_applications'
    )
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='player_applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'opportunity')
        ordering = ['-applied_at']
        verbose_name = "Trial Application"
        verbose_name_plural = "Trial Applications"

    def __str__(self):
        return f"{self.player.user.username} interested in {self.opportunity.title}"


# ===================================================================
# Follow System
# ===================================================================

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


class FollowRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_follow_requests'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_follow_requests'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


# ===================================================================
# Private Messaging
# ===================================================================

class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    def get_last_message(self):
        return self.messages.order_by('-sent_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def __str__(self):
        names = ', '.join(self.participants.values_list('username', flat=True))
        return f"Conversation: {names}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    body = models.TextField(max_length=2000)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.username}: {self.body[:50]}"


# ===================================================================
# Fan Profile
# ===================================================================

class FanProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fan_profile'
    )
    favourite_club = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fan: {self.user.username}"


# ===================================================================
# Scout Watchlist / Club Shortlist
# ===================================================================

class Watchlist(models.Model):
    """Used by scouts to privately track players of interest."""
    scout = models.ForeignKey(
        ScoutProfile,
        on_delete=models.CASCADE,
        related_name='watchlist'
    )
    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name='watchlisted_by'
    )
    private_notes = models.TextField(
        blank=True,
        help_text='Private scout notes — never shown to player'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['scout', 'player']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.scout.user.username} watching {self.player.user.username}"


class ClubShortlist(models.Model):
    """Used by clubs to shortlist players for opportunities."""
    club = models.ForeignKey(
        ClubProfile,
        on_delete=models.CASCADE,
        related_name='shortlist'
    )
    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name='shortlisted_by'
    )
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Optional — link shortlist to a specific trial'
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['club', 'player']

    def __str__(self):
        return f"{self.club.club_name} shortlisted {self.player.user.username}"
