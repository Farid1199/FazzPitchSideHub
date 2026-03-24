from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile,
    ManagerProfile, QualificationVerification, ScoutVerification, Opportunity, Post,
    FanProfile, ContactSubmission, Report
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
    Requires username, email, password, privacy consent, and community guidelines consent.
    """
    privacy_consent = forms.BooleanField(
        required=True,
        label='I agree to the Privacy Policy and consent to my data being processed',
        error_messages={'required': 'You must agree to the Privacy Policy to create an account.'},
    )
    community_guidelines_consent = forms.BooleanField(
        required=True,
        label='I agree to follow the Community Guidelines and Code of Conduct',
        error_messages={'required': 'You must agree to the Community Guidelines to create an account.'},
    )

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
            'date_of_birth',
            'position', 
            'current_team',
            'available_for_club',
            'availability_status',
            'bio',
            'location_postcode', 
            'playing_level', 
            'height', 
            'preferred_foot', 
            'youtube_highlight_url',
            'video_file',
            'previous_clubs',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'}),
            'previous_clubs': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A short professional bio shown on your profile...', 'maxlength': '500'}),
            'availability_status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
        }
        labels = {
            'date_of_birth': 'Date of Birth',
            'available_for_club': 'Looking for a Club (legacy)',
            'availability_status': 'Availability Status',
            'bio': 'Professional Bio',
            'current_team': 'Current Team/Club',
            'youtube_highlight_url': 'YouTube Highlights URL',
        }
        help_texts = {
            'date_of_birth': 'You must be at least 18 years old to register as a player.',
            'current_team': 'Leave blank if you are currently without a team.',
            'available_for_club': 'Legacy field — use Availability Status instead.',
            'availability_status': 'Set your current availability so scouts and clubs can see your status.',
            'bio': 'Write a short professional bio, or use the AI generator.',
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise ValidationError('You must be at least 18 years old to register as a player.')
            if dob > today:
                raise ValidationError('Date of birth cannot be in the future.')
        return dob

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
    Form for managers to upload coaching certificates for Fazz Pitchside verification.
    
    - Certificate image is ALWAYS required.
    - Dashboard screenshot and FA FAN Number are ONLY required when the
      qualification type is NOT 'NONE' (No Formal Qualification).
    """
    class Meta:
        model = QualificationVerification
        fields = [
            'qualification_type',
            'certificate_image',
            'dashboard_screenshot',
            'fa_fan_number',
        ]
        widgets = {
            'certificate_image': forms.FileInput(attrs={'accept': 'image/*,.pdf'}),
            'dashboard_screenshot': forms.FileInput(attrs={'accept': 'image/*'}),
            'fa_fan_number': forms.TextInput(attrs={
                'placeholder': 'e.g., FAN1234567',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
        }
        labels = {
            'qualification_type': 'Which Qualification Are You Verifying?',
            'certificate_image': 'Upload Certificate Photo/Scan',
            'dashboard_screenshot': 'Upload England Football Dashboard Screenshot',
            'fa_fan_number': 'FA FAN Number',
        }
        help_texts = {
            'certificate_image': 'Upload a clear photo or scan of your coaching certificate. Your full name and qualification level must be visible.',
            'dashboard_screenshot': 'Log into England Football Learning, take a screenshot showing your name, FAN number, and licence level.',
            'fa_fan_number': 'Your FA Football Affiliate Number. This must match the FAN shown on your dashboard screenshot.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make dashboard_screenshot and fa_fan_number not required at the field level;
        # we enforce them conditionally in clean() based on qualification_type.
        self.fields['dashboard_screenshot'].required = False
        self.fields['fa_fan_number'].required = False

    def clean_certificate_image(self):
        cert = self.cleaned_data.get('certificate_image')
        if not cert:
            raise ValidationError('Certificate image is required. You cannot submit for verification without it.')
        return cert

    def clean(self):
        cleaned_data = super().clean()
        qualification_type = cleaned_data.get('qualification_type')

        # If the manager selected an actual qualification (not NONE),
        # FAN number and dashboard screenshot become mandatory.
        if qualification_type and qualification_type != 'NONE':
            fan = cleaned_data.get('fa_fan_number', '').strip()
            screenshot = cleaned_data.get('dashboard_screenshot')

            if not fan:
                self.add_error('fa_fan_number', 'FA FAN Number is required when verifying a formal qualification.')
            if not screenshot:
                self.add_error('dashboard_screenshot', 'Dashboard screenshot is required when verifying a formal qualification.')

        return cleaned_data


class ScoutVerificationForm(forms.ModelForm):
    """
    Form for scouts to submit verification documents.

    Validation rules:
    - certificate_file: always required. Max 10 MB. PDF/JPG/PNG only.
    - qualification_body + qualification_level: always required.
    - If qualification_body == 'FA': fa_fan_number + dashboard_screenshot required.
    - If requested_tier in TIER2/TIER3: safeguarding_certificate + dbs_expiry_date required;
      dbs_expiry_date must be in the future.
    - If requested_tier == TIER3: club_affiliation_proof + sample_scout_report required.
    """

    _ALLOWED_CERT_TYPES = ('.pdf', '.jpg', '.jpeg', '.png')
    _ALLOWED_IMAGE_TYPES = ('.jpg', '.jpeg', '.png')
    _MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB

    class Meta:
        model = ScoutVerification
        fields = [
            'requested_tier',
            'qualification_body',
            'qualification_level',
            'fa_fan_number',
            'certificate_file',
            'dashboard_screenshot',
            'safeguarding_certificate',
            'dbs_expiry_date',
            'club_affiliation_proof',
            'sample_scout_report',
        ]
        widgets = {
            'requested_tier': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'id': 'id_requested_tier',
            }),
            'qualification_body': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'id': 'id_qualification_body',
            }),
            'qualification_level': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
            }),
            'fa_fan_number': forms.TextInput(attrs={
                'placeholder': 'e.g., FAN1234567',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
            }),
            'certificate_file': forms.FileInput(attrs={'accept': '.pdf,image/*'}),
            'dashboard_screenshot': forms.FileInput(attrs={'accept': 'image/*'}),
            'safeguarding_certificate': forms.FileInput(attrs={'accept': '.pdf,image/*'}),
            'dbs_expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
            }),
            'club_affiliation_proof': forms.FileInput(attrs={'accept': '.pdf,image/*'}),
            'sample_scout_report': forms.FileInput(attrs={'accept': '.pdf,image/*'}),
        }
        labels = {
            'requested_tier': 'Verification Tier Requested',
            'qualification_body': 'Awarding Body',
            'qualification_level': 'Qualification Level',
            'fa_fan_number': 'FA FAN Number',
            'certificate_file': 'Upload Certificate (PDF or Image)',
            'dashboard_screenshot': 'England Football Dashboard Screenshot',
            'safeguarding_certificate': 'Safeguarding Certificate (PDF or Image)',
            'dbs_expiry_date': 'DBS Certificate Expiry Date',
            'club_affiliation_proof': 'Club Affiliation Proof (PDF or Image)',
            'sample_scout_report': 'Sample Scouting Report (PDF or Image)',
        }
        help_texts = {
            'certificate_file': 'Clear scan or photo of your qualification certificate. Max 10 MB.',
            'dashboard_screenshot': 'Log into learn.englandfootball.com and screenshot your qualifications page.',
            'safeguarding_certificate': 'Required for Tier 2 and above. Max 10 MB.',
            'dbs_expiry_date': 'Required for Tier 2 and above. Must be a future date.',
            'club_affiliation_proof': 'Official signed letter from your club (Tier 3 only). Max 10 MB.',
            'sample_scout_report': 'Anonymised sample report demonstrating scouting knowledge (Tier 3 only). Max 10 MB.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All conditional fields are not required at the Django field level;
        # enforcement is done in clean() based on cross-field logic.
        conditional = [
            'fa_fan_number', 'dashboard_screenshot', 'safeguarding_certificate',
            'dbs_expiry_date', 'club_affiliation_proof', 'sample_scout_report',
        ]
        for field in conditional:
            self.fields[field].required = False

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #
    def _check_file_size(self, file, field_name):
        import os
        if file and hasattr(file, 'size') and file.size > self._MAX_FILE_BYTES:
            size_mb = file.size / (1024 * 1024)
            raise ValidationError(
                f'{field_name} must be under 10 MB. Your file is {size_mb:.1f} MB.'
            )

    def _check_file_extension(self, file, allowed_exts, field_name):
        import os
        if file and hasattr(file, 'name'):
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_exts:
                raise ValidationError(
                    f'{field_name}: unsupported file type "{ext}". '
                    f'Allowed: {", ".join(allowed_exts)}.'
                )

    def _validate_mime(self, file, allowed_mimes, field_name):
        """
        Server-side MIME validation using python-magic where available.
        Falls back to extension check if magic is not installed.
        """
        if not file:
            return
        try:
            import magic
            file.seek(0)
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            if mime not in allowed_mimes:
                raise ValidationError(
                    f'{field_name}: file content type "{mime}" is not allowed.'
                )
        except ImportError:
            pass  # python-magic not installed; extension check already performed

    # ------------------------------------------------------------------ #
    # Per-field clean methods                                              #
    # ------------------------------------------------------------------ #
    def clean_certificate_file(self):
        f = self.cleaned_data.get('certificate_file')
        if not f:
            raise ValidationError('Certificate file is required.')
        self._check_file_size(f, 'Certificate file')
        self._check_file_extension(f, self._ALLOWED_CERT_TYPES, 'Certificate file')
        self._validate_mime(
            f,
            {'application/pdf', 'image/jpeg', 'image/png'},
            'Certificate file'
        )
        return f

    def clean_dashboard_screenshot(self):
        f = self.cleaned_data.get('dashboard_screenshot')
        if f:
            self._check_file_size(f, 'Dashboard screenshot')
            self._check_file_extension(f, self._ALLOWED_IMAGE_TYPES, 'Dashboard screenshot')
            self._validate_mime(f, {'image/jpeg', 'image/png'}, 'Dashboard screenshot')
        return f

    def clean_safeguarding_certificate(self):
        f = self.cleaned_data.get('safeguarding_certificate')
        if f:
            self._check_file_size(f, 'Safeguarding certificate')
            self._check_file_extension(f, self._ALLOWED_CERT_TYPES, 'Safeguarding certificate')
            self._validate_mime(
                f,
                {'application/pdf', 'image/jpeg', 'image/png'},
                'Safeguarding certificate'
            )
        return f

    def clean_club_affiliation_proof(self):
        f = self.cleaned_data.get('club_affiliation_proof')
        if f:
            self._check_file_size(f, 'Club affiliation proof')
            self._check_file_extension(f, self._ALLOWED_CERT_TYPES, 'Club affiliation proof')
            self._validate_mime(
                f,
                {'application/pdf', 'image/jpeg', 'image/png'},
                'Club affiliation proof'
            )
        return f

    def clean_sample_scout_report(self):
        f = self.cleaned_data.get('sample_scout_report')
        if f:
            self._check_file_size(f, 'Sample scout report')
            self._check_file_extension(f, self._ALLOWED_CERT_TYPES, 'Sample scout report')
            self._validate_mime(
                f,
                {'application/pdf', 'image/jpeg', 'image/png'},
                'Sample scout report'
            )
        return f

    # ------------------------------------------------------------------ #
    # Cross-field validation                                               #
    # ------------------------------------------------------------------ #
    def clean(self):
        from django.utils import timezone
        cleaned_data = super().clean()

        qualification_body = cleaned_data.get('qualification_body')
        requested_tier = cleaned_data.get('requested_tier')

        # FA-specific fields
        if qualification_body == 'FA':
            if not cleaned_data.get('fa_fan_number', '').strip():
                self.add_error('fa_fan_number', 'FA FAN Number is required for FA qualifications.')
            if not cleaned_data.get('dashboard_screenshot'):
                self.add_error(
                    'dashboard_screenshot',
                    'England Football dashboard screenshot is required for FA qualifications.'
                )

        # Tier 2 + Tier 3 requirements
        if requested_tier in ('TIER2', 'TIER3'):
            if not cleaned_data.get('safeguarding_certificate'):
                self.add_error(
                    'safeguarding_certificate',
                    'Safeguarding certificate is required for Tier 2 and above.'
                )
            dbs_expiry = cleaned_data.get('dbs_expiry_date')
            if not dbs_expiry:
                self.add_error(
                    'dbs_expiry_date',
                    'DBS certificate expiry date is required for Tier 2 and above.'
                )
            elif dbs_expiry <= timezone.now().date():
                self.add_error(
                    'dbs_expiry_date',
                    'DBS certificate has expired. Please renew it before applying.'
                )

        # Tier 3 only requirements
        if requested_tier == 'TIER3':
            if not cleaned_data.get('club_affiliation_proof'):
                self.add_error(
                    'club_affiliation_proof',
                    'Club affiliation proof (signed letter or official email) is required for Tier 3.'
                )
            if not cleaned_data.get('sample_scout_report'):
                self.add_error(
                    'sample_scout_report',
                    'A sample anonymised scouting report is required for Tier 3.'
                )

        return cleaned_data


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
            'contract_type',
            'age_min',
            'age_max',
            'trial_date',
            'application_deadline',
            'positions_needed',
            'level_required',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide details about the trial...'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com/trial-info (optional)'}),
            'trial_date': forms.DateInput(attrs={'type': 'date'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'positions_needed': forms.TextInput(attrs={'placeholder': 'e.g. ST, CM, CB'}),
            'level_required': forms.TextInput(attrs={'placeholder': 'e.g. Step 3-4, Sunday League'}),
            'age_min': forms.NumberInput(attrs={'min': '14', 'max': '50', 'placeholder': 'Min age'}),
            'age_max': forms.NumberInput(attrs={'min': '14', 'max': '50', 'placeholder': 'Max age'}),
        }
        labels = {
            'title': 'Trial Title',
            'target_position': 'Primary Position Needed',
            'description': 'Trial Description',
            'link': 'More Information Link (Optional)',
            'contract_type': 'Contract Type',
            'age_min': 'Minimum Age',
            'age_max': 'Maximum Age',
            'trial_date': 'Trial Date',
            'application_deadline': 'Application Deadline',
            'positions_needed': 'All Positions Needed',
            'level_required': 'Level/Standard Required',
        }
        help_texts = {
            'title': 'e.g., "Striker Trial - Open Day"',
            'target_position': 'e.g., "Striker", "Midfielder", "All Positions"',
            'description': 'Include any additional details players should know.',
            'link': 'Link to your website or social media post with more details.',
            'contract_type': 'What type of contract is offered?',
            'trial_date': 'Date of the trial.',
            'application_deadline': 'Last date to apply.',
            'positions_needed': 'Comma-separated list of all positions you need.',
            'level_required': 'Minimum playing standard expected.',
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
            # Achievement fields (for players)
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
            # Manager-specific fields
            'tactical_analysis',
            'team_formation',
            'team_performance',
            'coaching_methodology',
            # Scout-specific fields
            'player_scouted',
            'player_position',
            'player_age',
            'player_club',
            'scouting_report',
            'strengths',
            'areas_for_improvement',
            'potential_rating',
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
            # Manager-specific widgets
            'tactical_analysis': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Share your tactical insights, game analysis, or coaching observations...'
            }),
            'team_formation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., 4-3-3, 3-5-2, 4-2-3-1'
            }),
            'team_performance': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Describe team performance, key moments, or player contributions...'
            }),
            'coaching_methodology': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Share your coaching methods, training philosophy, or development approach...'
            }),
            # Scout-specific widgets
            'player_scouted': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Player name'
            }),
            'player_position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'e.g., ST, CM, CB'
            }),
            'player_age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'min': '10',
                'max': '50',
                'placeholder': 'e.g., 18'
            }),
            'player_club': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Current club'
            }),
            'scouting_report': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Detailed scouting report and overall assessment...'
            }),
            'strengths': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': "Player's key strengths and standout qualities..."
            }),
            'areas_for_improvement': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Areas where the player can develop further...'
            }),
            'potential_rating': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'step': '0.1',
                'min': '0',
                'max': '10',
                'placeholder': 'e.g., 7.5'
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
            # Manager labels
            'tactical_analysis': 'Tactical Analysis',
            'team_formation': 'Formation Used',
            'team_performance': 'Team Performance',
            'coaching_methodology': 'Coaching Methodology',
            # Scout labels
            'player_scouted': 'Player Name',
            'player_position': 'Position',
            'player_age': 'Age',
            'player_club': 'Current Club',
            'scouting_report': 'Scouting Report',
            'strengths': 'Key Strengths',
            'areas_for_improvement': 'Areas for Improvement',
            'potential_rating': 'Potential Rating (out of 10)',
        }


class FanProfileForm(forms.ModelForm):
    """
    Form for creating/updating a Fan Profile.
    """
    class Meta:
        model = FanProfile
        fields = ['favourite_club', 'location', 'bio']
        widgets = {
            'favourite_club': forms.TextInput(attrs={
                'placeholder': 'e.g., Halesowen Town FC',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g., Birmingham',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Tell us about yourself...',
                'maxlength': '300',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
        }
        labels = {
            'favourite_club': 'Favourite Club',
            'location': 'Location',
            'bio': 'About You',
        }


class ContactForm(forms.ModelForm):
    """
    Public contact form for users to reach Fazz PitchSide Hub.
    Covers feedback, bug reports, partnership inquiries, support, and GDPR requests.
    """
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'category', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Brief summary of your message',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell us more about your question, feedback, or request...',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'category': 'What is this about?',
            'subject': 'Subject',
            'message': 'Your Message',
        }

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if len(message.strip()) < 20:
            raise ValidationError('Please provide a bit more detail so we can help you properly (at least 20 characters).')
        return message


class ReportForm(forms.ModelForm):
    """
    Form for users to report posts, comments, or other users.
    Used for community moderation and content safety.
    """
    class Meta:
        model = Report
        fields = ['reason', 'description', 'screenshot']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Please describe the issue in detail. What happened? Why do you believe this violates our Community Guidelines?',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'maxlength': '2000',
            }),
            'screenshot': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            }),
        }
        labels = {
            'reason': 'Reason for Report',
            'description': 'Describe the Issue',
            'screenshot': 'Screenshot (Optional)',
        }
        help_texts = {
            'description': 'The more detail you provide, the faster we can review and act on your report.',
            'screenshot': 'If you have a screenshot of the issue, it can help us review your report faster.',
        }

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description.strip()) < 20:
            raise ValidationError('Please provide more detail about the issue (at least 20 characters).')
        if len(description) > 2000:
            raise ValidationError('Description must be under 2000 characters.')
        return description
