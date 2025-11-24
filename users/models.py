from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Acts as the base user for authentication.
    """
    USER_TYPE_CHOICES = [
        ('UNASSIGNED', 'Unassigned'),
        ('PLAYER', 'Player'),
        ('CLUB', 'Club'),
        ('SCOUT', 'Scout'),
    ]

    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='UNASSIGNED',
        help_text="The role of the user in the system."
    )
    is_role_selected = models.BooleanField(
        default=False,
        help_text="Designates whether the user has selected a role."
    )

    def __str__(self):
        return self.username


class PlayerProfile(models.Model):
    """
    Profile model for Players.
    Linked to CustomUser via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='player_profile')
    position = models.CharField(max_length=50, help_text="Primary playing position (e.g., Striker, Goalkeeper).")
    height = models.DecimalField(max_digits=4, decimal_places=2, help_text="Height in meters.", null=True, blank=True)
    playing_level = models.CharField(max_length=100, help_text="Current playing level (e.g., Step 5, Sunday League).")
    previous_clubs = models.TextField(blank=True, help_text="List of previous clubs.")

    def __str__(self):
        return f"Player: {self.user.username}"


class ClubProfile(models.Model):
    """
    Profile model for Clubs.
    Linked to CustomUser via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='club_profile')
    club_name = models.CharField(max_length=100, help_text="Official name of the club.")
    league = models.CharField(max_length=100, help_text="League the club currently plays in.")
    location = models.CharField(max_length=100, help_text="City or region of the club.")
    founded_year = models.PositiveIntegerField(help_text="Year the club was founded.", null=True, blank=True)

    def __str__(self):
        return f"Club: {self.club_name}"


class ScoutProfile(models.Model):
    """
    Profile model for Scouts.
    Linked to CustomUser via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='scout_profile')
    organization = models.CharField(max_length=100, blank=True, help_text="Organization or Club the scout works for.")
    region = models.CharField(max_length=100, help_text="Primary region covered by the scout.")

    def __str__(self):
        return f"Scout: {self.user.username}"

# --- Existing models commented out for initial structure setup ---
# class Media(models.Model):
#     ...
# class Trial(models.Model):
#     ...
# class TrialApplication(models.Model):
#     ...
# class Endorsement(models.Model):
#     ...
# class Message(models.Model):
#     ...
# class Notification(models.Model):
#     ...
# class Post(models.Model):
#     ...
