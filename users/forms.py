from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Trial, Message, Media, Endorsement

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].widget.choices = [
            ('PLAYER', 'Player'),
            ('CLUB', 'Club/Team'),
            ('COACH', 'Coach'),
            ('SCOUT', 'Scout'),
            ('VOLUNTEER', 'Volunteer'),
        ]

class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'bio', 'location', 
            'phone_number', 'website', 'date_of_birth', 'position', 
            'playing_level', 'previous_clubs', 'founded_year', 'club_type',
            'profile_image', 'profile_visibility'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'previous_clubs': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance')
        if user:
            # Show relevant fields based on user type
            if user.user_type == 'PLAYER':
                self.fields.pop('founded_year', None)
                self.fields.pop('club_type', None)
            elif user.user_type == 'CLUB':
                self.fields.pop('position', None)
                self.fields.pop('playing_level', None)
                self.fields.pop('previous_clubs', None)
                self.fields.pop('date_of_birth', None)


class TrialForm(forms.ModelForm):
    class Meta:
        model = Trial
        fields = ['title', 'description', 'location', 'date', 'positions_needed', 'age_range', 'is_public']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['media_type', 'title', 'description', 'url', 'file', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].help_text = "For videos: YouTube URL. Leave empty if uploading file."
        self.fields['file'].help_text = "Upload image or video file. Leave empty if using URL."


class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your endorsement...'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search players, clubs, coaches...'})
    )
    user_type = forms.ChoiceField(
        choices=[('', 'All Types')] + CustomUser.USER_TYPE_CHOICES[:5],  # Exclude VISITOR
        required=False
    )
    location = forms.CharField(max_length=100, required=False)
    position = forms.CharField(max_length=50, required=False)  # For players
    verified_only = forms.BooleanField(required=False, label="Verified users only")


class TrialApplicationForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Tell the club why you're interested in this trial",
        required=False
    )
