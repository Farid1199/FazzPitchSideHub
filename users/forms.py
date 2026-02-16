from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile, 
    ManagerProfile, QualificationVerification, Opportunity, Post
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


class OpportunityForm(forms.ModelForm):
    """
    Form for clubs to post trial opportunities.
    """
    published_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Trial Date & Time',
        help_text='When is the trial taking place?'
    )
    
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'target_position',
            'description',
            'published_date',
            'link',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide details about the trial...'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com/trial-info (optional)'}),
        }
        labels = {
            'title': 'Trial Title',
            'target_position': 'Position Needed',
            'description': 'Trial Description',
            'link': 'More Information Link (Optional)',
        }
        help_texts = {
            'title': 'e.g., "Striker Trial - Open Day"',
            'target_position': 'e.g., "Striker", "Midfielder", "All Positions"',
            'description': 'Include any additional details players should know.',
            'link': 'Link to your website or social media post with more details.',
        }


class PostForm(forms.ModelForm):
    """
    Form for creating social media-style posts.
    Used by Players, Managers, and Scouts to share achievements, highlights, and updates.
    """
    video = forms.FileField(
        required=False,
        validators=[validate_video_file_size, validate_video_file_extension],
        help_text='Upload a video (MP4, AVI, MOV, etc.). Maximum file size: 50MB.',
        widget=forms.FileInput(attrs={'accept': 'video/*', 'class': 'hidden'})
    )
    
    class Meta:
        model = Post
        fields = [
            'post_type',
            'caption',
            'image',
            'video',
            'youtube_url',
            # Achievement fields
            'goals',
            'assists',
            'clean_sheets',
            'minutes_played',
            'match_rating',
            # Match details
            'match_opponent',
            'match_result',
            'match_date',
            'competition',
            # Award/Milestone
            'award_title',
            'award_description',
        ]
        widgets = {
            'caption': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'Share your football story... achievements, highlights, match reports, or updates!'
            }),
            'post_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'hidden'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'YouTube video URL (optional)'
            }),
            'goals': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'min': '0',
                'placeholder': '0'
            }),
            'assists': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'min': '0',
                'placeholder': '0'
            }),
            'clean_sheets': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'min': '0',
                'placeholder': '0'
            }),
            'minutes_played': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'min': '0',
                'placeholder': 'e.g., 90'
            }),
            'match_rating': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'step': '0.1',
                'min': '0',
                'max': '10',
                'placeholder': 'e.g., 8.5'
            }),
            'match_opponent': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'e.g., Manchester United'
            }),
            'match_result': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'e.g., Won 3-1'
            }),
            'match_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'type': 'date'
            }),
            'competition': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'e.g., FA Cup, Premier League'
            }),
            'award_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'e.g., Player of the Month'
            }),
            'award_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'Describe your achievement...'
            }),
        }
        labels = {
            'post_type': 'Post Type',
            'caption': 'Caption',
            'image': 'Upload Image',
            'video': 'Upload Video',
            'youtube_url': 'YouTube Video URL',
            'goals': 'Goals',
            'assists': 'Assists',
            'clean_sheets': 'Clean Sheets',
            'minutes_played': 'Minutes Played',
            'match_rating': 'Match Rating (out of 10)',
            'match_opponent': 'Opponent',
            'match_result': 'Match Result',
            'match_date': 'Match Date',
            'competition': 'Competition',
            'award_title': 'Award/Milestone Title',
            'award_description': 'Description',
        }
