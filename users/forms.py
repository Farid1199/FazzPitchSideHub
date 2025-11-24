from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PlayerProfile, ClubProfile, ScoutProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering a new user.
    Only asks for username, email, and password.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class PlayerProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Player Profile.
    """
    class Meta:
        model = PlayerProfile
        fields = ['position', 'height', 'playing_level', 'previous_clubs']
        widgets = {
            'previous_clubs': forms.Textarea(attrs={'rows': 3}),
        }

class ClubProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Club Profile.
    """
    class Meta:
        model = ClubProfile
        fields = ['club_name', 'league', 'location', 'founded_year']

class ScoutProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Scout Profile.
    """
    class Meta:
        model = ScoutProfile
        fields = ['organization', 'region']

