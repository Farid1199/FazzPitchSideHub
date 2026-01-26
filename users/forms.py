from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PlayerProfile, ClubProfile, ScoutProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering a new user.
    Only asks for username, email, and password.
    """
    class Meta:
        model = User
        fields = ['username', 'email']

class PlayerProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Player Profile.
    """
    class Meta:
        model = PlayerProfile
        fields = [
            'position', 
            'location_postcode', 
            'playing_level', 
            'height', 
            'preferred_foot', 
            'youtube_highlight_url', 
            'previous_clubs'
        ]
        widgets = {
            'previous_clubs': forms.Textarea(attrs={'rows': 3}),
        }

class ClubProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Club Profile.
    Used when clubs sign up and create their profiles.
    """
    class Meta:
        model = ClubProfile
        fields = [
            'club_name', 
            'league_level', 
            'location_postcode',
            'league',
            'location',
            'rss_feed_url',
            'founded_year'
        ]
        
class AdminClubForm(forms.ModelForm):
    """
    Form for admins to add clubs without user accounts.
    """
    class Meta:
        model = ClubProfile
        fields = [
            'club_name',
            'league_level',
            'location_postcode',
            'location',
            'league',
            'founded_year',
            'rss_feed_url',
        ]
        widgets = {
            'rss_feed_url': forms.URLInput(attrs={'size': 60}),
        }

class ScoutProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Scout Profile.
    """
    class Meta:
        model = ScoutProfile
        fields = ['organization', 'region']

