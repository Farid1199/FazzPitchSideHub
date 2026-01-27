from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile, 
    ManagerProfile, QualificationVerification
)

def validate_video_file_size(file):
    """Validate that video file is not larger than 50MB"""
    max_size_mb = 50
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB. Your file is {file.size / (1024 * 1024):.1f}MB.')
    return file

def validate_video_file_extension(file):
    """Validate that file has an allowed video extension"""
    import os
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
    if ext not in valid_extensions:
        raise ValidationError(f'File type not supported. Please upload a video file ({", ".join(valid_extensions)}).')
    return file

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
    video_file = forms.FileField(
        required=False,
        validators=[validate_video_file_size, validate_video_file_extension],
        help_text='Upload a highlight video (MP4, AVI, MOV, etc.). Maximum file size: 50MB.',
        widget=forms.FileInput(attrs={'accept': 'video/*'})
    )
    
    class Meta:
        model = PlayerProfile
        fields = [
            'position', 
            'current_team',
            'available_for_club',
            'location_postcode', 
            'playing_level', 
            'height', 
            'preferred_foot', 
            'youtube_highlight_url',
            'video_file',
            'previous_clubs',
        ]
        widgets = {
            'previous_clubs': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'available_for_club': 'Looking for a Club',
            'current_team': 'Current Team/Club',
            'youtube_highlight_url': 'YouTube Highlights URL',
        }
        help_texts = {
            'current_team': 'Leave blank if you are currently without a team.',
            'available_for_club': 'Check this box if you are actively looking for a new club.',
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


class ManagerProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Manager Profile.
    """
    class Meta:
        model = ManagerProfile
        fields = [
            'club_name',
            'current_role',
            'availability',
            'location_postcode',
            'coaching_philosophy',
            'preferred_formation',
            'years_of_experience',
            'career_history',
            'achievements',
            'games_managed',
            'win_rate',
            'highest_qualification',
            'additional_badges',
        ]
        widgets = {
            'coaching_philosophy': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your coaching style and philosophy...'}),
            'career_history': forms.Textarea(attrs={'rows': 5, 'placeholder': 'List your previous clubs, roles, and dates...'}),
            'achievements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List trophies, titles, and notable achievements...'}),
            'additional_badges': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., FA Youth Award, Goalkeeping Level 2...'}),
        }
        labels = {
            'club_name': 'Current Club',
            'current_role': 'Current Role/Position',
            'win_rate': 'Win Rate (%)',
            'highest_qualification': 'Highest Coaching Qualification',
        }
        help_texts = {
            'club_name': 'Leave blank if not currently employed.',
            'win_rate': 'Enter as a percentage (e.g., 65.5 for 65.5%).',
        }


class QualificationVerificationForm(forms.ModelForm):
    """
    Form for managers to upload coaching certificates for verification.
    """
    class Meta:
        model = QualificationVerification
        fields = [
            'qualification_type',
            'certificate_image',
            'fa_fan_number',
        ]
        widgets = {
            'certificate_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'qualification_type': 'Which Qualification Are You Verifying?',
            'certificate_image': 'Upload Certificate Photo/Scan',
            'fa_fan_number': 'FA FAN Number (Optional)',
        }
        help_texts = {
            'certificate_image': 'Take a clear photo or scan of your coaching certificate.',
            'fa_fan_number': 'Your FA Football Affiliate Number, if you have one.',
        }


