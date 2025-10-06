from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone


# Create your models here.

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('PLAYER', 'Player'),
        ('CLUB', 'Club/Team'),
        ('COACH', 'Coach'),
        ('SCOUT', 'Scout'),
        ('VOLUNTEER', 'Volunteer'),
        ('VISITOR', 'Visitor'),  # Added for public users
    ]
    
    PRIVACY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
        ('VERIFIED_ONLY', 'Verified Scouts Only'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Social Platform Features
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_visibility = models.CharField(max_length=15, choices=PRIVACY_CHOICES, default='PUBLIC')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Player-specific fields
    position = models.CharField(max_length=50, blank=True, null=True)
    playing_level = models.CharField(max_length=100, blank=True, null=True)
    previous_clubs = models.TextField(blank=True, null=True, help_text="Comma-separated list of previous clubs")
    
    # Club-specific fields
    founded_year = models.IntegerField(blank=True, null=True)
    club_type = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_absolute_url(self):
        """Generate public profile URL"""
        return reverse('public_profile', kwargs={'username': self.username})
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('VIDEO', 'Video'),
        ('IMAGE', 'Image'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(help_text="YouTube URL for videos or image URL")
    file = models.FileField(upload_to='media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Trial(models.Model):
    club = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trials')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    positions_needed = models.CharField(max_length=200, blank=True, null=True)
    age_range = models.CharField(max_length=50, blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.title} - {self.club.username}"


class TrialApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name='applications')
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trial_applications')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['trial', 'player']
    
    def __str__(self):
        return f"{self.player.username} -> {self.trial.title}"


class Endorsement(models.Model):
    endorser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_endorsements')
    endorsed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_endorsements')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['endorser', 'endorsed']
    
    def __str__(self):
        return f"{self.endorser.username} endorsed {self.endorsed.username}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.subject}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('TRIAL_POSTED', 'Trial Posted'),
        ('PROFILE_VIEW', 'Profile Viewed'),
        ('MESSAGE_RECEIVED', 'Message Received'),
        ('ENDORSEMENT', 'Endorsement Received'),
        ('TRIAL_APPLICATION', 'Trial Application'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Post(models.Model):
    POST_TYPES = [
        ('UPDATE', 'General Update'),
        ('TRIAL', 'Trial Posted'),
        ('MEDIA', 'Media Upload'),
        ('ENDORSEMENT', 'Endorsement'),
    ]
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=15, choices=POST_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    # Optional relations
    related_trial = models.ForeignKey(Trial, on_delete=models.CASCADE, blank=True, null=True)
    related_media = models.ForeignKey(Media, on_delete=models.CASCADE, blank=True, null=True)
    related_endorsement = models.ForeignKey(Endorsement, on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username}: {self.post_type} post"