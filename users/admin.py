from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile,
    ManagerProfile, QualificationVerification, ClubSource, NewsItem, Opportunity, Post,
    Comment, ScoutVerification, Notification,
    Follow, FollowRequest, Conversation, Message, FanProfile, Watchlist, ClubShortlist,
    PlayerStats, ContactSubmission, Report,
)

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email']

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'playing_level']
    search_fields = ['user__username', 'position']


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'season', 'appearances', 'goals', 'assists', 'updated_at']
    list_filter = ['season']
    search_fields = ['player__user__username']
    raw_id_fields = ['player']

@admin.register(ClubProfile)
class ClubProfileAdmin(admin.ModelAdmin):
    list_display = ['club_name', 'league_level', 'location', 'rss_status', 'is_registered', 'news_count']
    list_filter = ['league_level', 'is_registered', 'location']
    search_fields = ['club_name', 'league', 'location']
    readonly_fields = ['is_registered']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('club_name', 'league_level', 'league', 'location', 'location_postcode', 'founded_year'),
            'description': 'Enter the basic details for the club.'
        }),
        ('Website & Media', {
            'fields': ('website_url', 'logo_url'),
            'description': 'Add the club\'s official website and logo image URL.'
        }),
        ('RSS Feed Configuration', {
            'fields': ('rss_feed_url',),
            'description': '<strong>Important:</strong> Add the club\'s RSS feed URL here to automatically fetch news and trial opportunities. '
                          'This will populate the Feeds page with live updates from the club\'s website. '
                          '<br><br><em>Example URLs:</em><br>'
                          '• https://clubwebsite.com/feed/<br>'
                          '• https://clubwebsite.com/rss/<br>'
                          '• https://clubwebsite.com/news/feed/'
        }),
        ('User Account', {
            'fields': ('user', 'is_registered'),
            'description': 'Link to user account if club has signed up. Leave blank for admin-added clubs.',
            'classes': ('collapse',)
        }),
    )
    
    def rss_status(self, obj):
        if obj.rss_feed_url:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ RSS Enabled</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ No RSS Feed</span>'
        )
    rss_status.short_description = 'RSS Feed Status'
    
    def news_count(self, obj):
        count = obj.news_items.count()
        if count > 0:
            return format_html(
                '<a href="/admin/users/newsitem/?club__id__exact={}">{} news items</a>',
                obj.id, count
            )
        return "0 news items"
    news_count.short_description = 'News Articles'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(ClubSource)
class ClubSourceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing RSS feed sources.
    These are clubs added by admins for RSS aggregation, separate from registered users.
    """
    list_display = ['name', 'league_level', 'rss_status', 'region', 'news_count', 'created_at']
    list_filter = ['league_level', 'region']
    search_fields = ['name', 'website_url']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'league_level', 'region'),
            'description': 'Enter the basic details for the club RSS source.'
        }),
        ('Website & Media', {
            'fields': ('website_url', 'logo_url'),
            'description': 'Add the club\'s official website and logo image URL.'
        }),
        ('RSS Feed Configuration', {
            'fields': ('rss_url',),
            'description': '<strong>Important:</strong> Add the club\'s RSS feed URL here to automatically fetch news and trial opportunities. '
                          '<br><br><em>Example URLs:</em><br>'
                          '• https://clubwebsite.com/feed/<br>'
                          '• https://clubwebsite.com/rss/<br>'
                          '• https://clubwebsite.com/news/feed/'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def rss_status(self, obj):
        if obj.rss_url:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ RSS Enabled</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ No RSS Feed</span>'
        )
    rss_status.short_description = 'RSS Feed Status'
    
    def news_count(self, obj):
        count = obj.news_items.count()
        if count > 0:
            return format_html(
                '<a href="/admin/users/newsitem/?source__id__exact={}">{} news items</a>',
                obj.id, count
            )
        return "0 news items"
    news_count.short_description = 'News Articles'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(ScoutProfile)
class ScoutProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'region']
    search_fields = ['user__username', 'organization']


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'club_name', 'current_role', 'highest_qualification', 'qualification_verified', 'availability']
    list_filter = ['highest_qualification', 'qualification_verified', 'availability']
    search_fields = ['user__username', 'club_name', 'current_role']
    readonly_fields = ['qualification_verified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'club_name', 'current_role', 'location_postcode', 'availability')
        }),
        ('Coaching Details', {
            'fields': ('coaching_philosophy', 'preferred_formation', 'years_of_experience')
        }),
        ('Career History', {
            'fields': ('career_history', 'achievements')
        }),
        ('Statistics', {
            'fields': ('games_managed', 'win_rate')
        }),
        ('Qualifications', {
            'fields': ('highest_qualification', 'additional_badges', 'qualification_verified'),
            'description': 'Qualification verification is handled through the QualificationVerification model.'
        }),
    )


@admin.register(QualificationVerification)
class QualificationVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for reviewing Coaching Licence Verification requests.
    
    FAZZ PITCHSIDE VERIFICATION CHECKLIST:
    1. Name Match — Does the name on the certificate match the profile?
    2. Certificate Format — Does it look consistent with FA/England Football templates?
    3. Issue Date Realism — Is the date realistic for the level claimed?
    4. FAN Consistency — Does the FAN on the dashboard match what they entered?
    5. Dashboard Cross-Check — Does the dashboard show the same licence level?
    6. Reverse Image Search — If suspicious, check certificate via Google Images.
    
    IMPORTANT: This is a Fazz Pitchside platform verification.
    NEVER claim 'FA Verified' or use FA branding.
    """
    list_display = [
        'manager_name', 'qualification_type', 'fan_number_display',
        'status_badge', 'submitted_at', 'reviewed_by', 'action_buttons'
    ]
    list_filter = ['status', 'qualification_type', 'submitted_at']
    search_fields = ['manager__user__username', 'fa_fan_number', 'manager__user__first_name', 'manager__user__last_name']
    readonly_fields = [
        'manager', 'submitted_at', 'certificate_preview', 
        'dashboard_preview', 'verification_checklist_display'
    ]
    date_hierarchy = 'submitted_at'
    list_per_page = 25
    
    fieldsets = (
        ('⚽ Verification Checklist (Read Before Approving)', {
            'fields': ('verification_checklist_display',),
            'description': '<div style="background:#fffbeb;border:2px solid #f59e0b;padding:16px;border-radius:8px;margin-bottom:12px;">'
                          '<strong style="color:#92400e;font-size:14px;">⚠️ FAZZ PITCHSIDE VERIFICATION — NOT AN OFFICIAL FA ENDORSEMENT</strong><br><br>'
                          '<strong>Before approving, check ALL of the following:</strong><br>'
                          '1️⃣ <strong>Name Match</strong> — Does the name on the certificate match the manager\'s profile name?<br>'
                          '2️⃣ <strong>Certificate Format</strong> — Does the certificate look consistent with known FA/England Football templates?<br>'
                          '3️⃣ <strong>Issue Date</strong> — Is the issue date realistic for the licence level claimed?<br>'
                          '4️⃣ <strong>FAN Consistency</strong> — Does the FAN number on the dashboard screenshot match the one entered in the form?<br>'
                          '5️⃣ <strong>Dashboard Cross-Check</strong> — Does the England Football Learning dashboard screenshot show the same name + licence level?<br>'
                          '6️⃣ <strong>Reverse Image Search</strong> — For UEFA B/A/Pro claims, right-click the certificate and run a Google reverse image search.<br><br>'
                          '<strong style="color:#dc2626;">🔴 For UEFA B and above: Apply extra scrutiny. These are elite claims.</strong>'
                          '</div>'
        }),
        ('📋 Verification Request', {
            'fields': ('manager', 'qualification_type', 'fa_fan_number', 'status', 'submitted_at')
        }),
        ('📄 Certificate (Document 1 of 2)', {
            'fields': ('certificate_preview', 'certificate_image'),
            'description': 'Review the coaching certificate. Check that the name, qualification level, and issue date are visible and realistic.'
        }),
        ('📊 England Football Dashboard Screenshot (Document 2 of 2)', {
            'fields': ('dashboard_preview', 'dashboard_screenshot'),
            'description': 'Review the England Football Learning dashboard screenshot. The FAN number, name, and licence level should match the certificate and form data.'
        }),
        ('✅ Admin Decision', {
            'fields': ('admin_notes', 'rejection_reason', 'verified_by', 'reviewed_at'),
            'description': '<strong>admin_notes</strong> = Internal only (manager cannot see this).<br>'
                          '<strong>rejection_reason</strong> = Visible to the manager if rejected (tell them what to fix).<br>'
                          '<strong>verified_by</strong> = Auto-filled when you use the bulk action, or set manually.'
        }),
    )
    
    actions = ['approve_verification', 'reject_verification', 'flag_for_review']
    
    def manager_name(self, obj):
        full_name = obj.manager.user.get_full_name()
        username = obj.manager.user.username
        return f"{full_name} ({username})" if full_name.strip() else username
    manager_name.short_description = 'Manager'
    manager_name.admin_order_field = 'manager__user__username'
    
    def fan_number_display(self, obj):
        if obj.fa_fan_number:
            return format_html('<code style="background:#f3f4f6;padding:2px 8px;border-radius:4px;">{}</code>', obj.fa_fan_number)
        return format_html('<span style="color:#ef4444;">❌ Missing</span>')
    fan_number_display.short_description = 'FAN Number'
    
    def status_badge(self, obj):
        colours = {
            'PENDING': ('#f59e0b', '#fffbeb', '⏳'),
            'APPROVED': ('#059669', '#ecfdf5', '✅'),
            'REJECTED': ('#dc2626', '#fef2f2', '❌'),
            'FLAGGED': ('#7c3aed', '#f5f3ff', '🚩'),
        }
        bg, bg_light, icon = colours.get(obj.status, ('#6b7280', '#f9fafb', '❓'))
        return format_html(
            '<span style="background:{};color:{};padding:4px 12px;border-radius:12px;font-size:12px;font-weight:bold;">'
            '{} {}</span>',
            bg_light, bg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def reviewed_by(self, obj):
        if obj.verified_by:
            return obj.verified_by.username
        return "-"
    reviewed_by.short_description = 'Reviewed By'
    
    def certificate_preview(self, obj):
        if obj.certificate_image:
            return format_html(
                '<div style="border:2px solid #d1d5db;border-radius:8px;padding:8px;display:inline-block;">'
                '<img src="{}" style="max-width:500px;max-height:400px;border-radius:4px;"/>'
                '<br><a href="{}" target="_blank" style="color:#2563eb;font-weight:bold;">'
                '📥 Open Full Size in New Tab</a></div>',
                obj.certificate_image.url, obj.certificate_image.url
            )
        return "No certificate uploaded"
    certificate_preview.short_description = 'Certificate Preview'
    
    def dashboard_preview(self, obj):
        if obj.dashboard_screenshot:
            return format_html(
                '<div style="border:2px solid #d1d5db;border-radius:8px;padding:8px;display:inline-block;">'
                '<img src="{}" style="max-width:500px;max-height:400px;border-radius:4px;"/>'
                '<br><a href="{}" target="_blank" style="color:#2563eb;font-weight:bold;">'
                '📥 Open Full Size in New Tab</a></div>',
                obj.dashboard_screenshot.url, obj.dashboard_screenshot.url
            )
        return "No dashboard screenshot uploaded"
    dashboard_preview.short_description = 'Dashboard Screenshot Preview'
    
    def verification_checklist_display(self, obj):
        fan_match = '⚠️ Check manually' if obj.fa_fan_number else '❌ No FAN provided'
        return format_html(
            '<div style="font-size:13px;line-height:1.8;">'
            '<strong>Manager:</strong> {} (username: {})<br>'
            '<strong>Claimed Qualification:</strong> {}<br>'
            '<strong>FAN Number Entered:</strong> <code>{}</code><br>'
            '<strong>FAN Consistency:</strong> {} — compare with dashboard screenshot<br>'
            '<strong>Dashboard Uploaded:</strong> {}<br>'
            '<strong>Certificate Uploaded:</strong> {}<br>'
            '</div>',
            obj.manager.user.get_full_name() or obj.manager.user.username,
            obj.manager.user.username,
            obj.get_qualification_type_display(),
            obj.fa_fan_number or 'N/A',
            fan_match,
            '✅ Yes' if obj.dashboard_screenshot else '❌ No',
            '✅ Yes' if obj.certificate_image else '❌ No',
        )
    verification_checklist_display.short_description = 'Quick Summary'
    
    def action_buttons(self, obj):
        if obj.status == 'PENDING':
            return format_html(
                '<a class="button" style="background:#059669;color:white;padding:4px 12px;border-radius:4px;text-decoration:none;margin-right:4px;" '
                'href="/admin/users/qualificationverification/{}/change/">📋 Review Now</a>',
                obj.pk
            )
        elif obj.status == 'FLAGGED':
            return format_html(
                '<a class="button" style="background:#7c3aed;color:white;padding:4px 12px;border-radius:4px;text-decoration:none;" '
                'href="/admin/users/qualificationverification/{}/change/">🚩 Review Flag</a>',
                obj.pk
            )
        return format_html('<span style="color:#6b7280;">{}</span>', obj.get_status_display())
    action_buttons.short_description = 'Actions'
    
    def approve_verification(self, request, queryset):
        """Bulk action: Approve selected verifications."""
        for verification in queryset:
            verification.status = 'APPROVED'
            verification.reviewed_at = timezone.now()
            verification.verified_by = request.user
            verification.save()
            # Update the manager's profile
            manager = verification.manager
            manager.qualification_verified = True
            manager.save()
        self.message_user(
            request, 
            f"✅ {queryset.count()} verification(s) approved as Fazz Pitchside Verified."
        )
    approve_verification.short_description = "✅ Approve selected — Mark as Fazz Pitchside Verified"
    
    def reject_verification(self, request, queryset):
        """Bulk action: Reject selected verifications."""
        for verification in queryset:
            verification.status = 'REJECTED'
            verification.reviewed_at = timezone.now()
            verification.verified_by = request.user
            if not verification.rejection_reason:
                verification.rejection_reason = 'Your submitted documents did not pass our verification checks. Please resubmit with clearer documentation.'
            verification.save()
        self.message_user(
            request, 
            f"❌ {queryset.count()} verification(s) rejected."
        )
    reject_verification.short_description = "❌ Reject selected verifications"
    
    def flag_for_review(self, request, queryset):
        """Bulk action: Flag selected for further review."""
        queryset.update(
            status='FLAGGED',
            reviewed_at=timezone.now()
        )
        self.message_user(
            request, 
            f"🚩 {queryset.count()} verification(s) flagged for further review."
        )
    flag_for_review.short_description = "🚩 Flag selected for further review"


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'club_link', 'league_display', 'published_date', 'created_at']
    list_filter = ['published_date', 'source__league_level', 'club__league_level', 'source', 'club']
    search_fields = ['title', 'description', 'source__name', 'club__club_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
    ordering = ['-published_date']
    
    def club_link(self, obj):
        club_name = obj.get_club_name()
        if obj.source:
            return format_html(
                '<a href="/admin/users/clubsource/{}/change/">{}</a> <span style="color: #3b82f6;">(RSS)</span>',
                obj.source.id, club_name
            )
        elif obj.club:
            return format_html(
                '<a href="/admin/users/clubprofile/{}/change/">{}</a> <span style="color: #10b981;">(User)</span>',
                obj.club.id, club_name
            )
        return club_name
    club_link.short_description = 'Club'
    
    def league_display(self, obj):
        return obj.get_league_display()
    league_display.short_description = 'League Level'
    
    fieldsets = (
        ('News Information', {
            'fields': ('title', 'link', 'description')
        }),
        ('Source Selection', {
            'fields': ('source', 'club'),
            'description': '<strong>Choose ONE source:</strong><br>'
                          '• <strong>Source (RSS):</strong> For news automatically fetched from RSS feeds<br>'
                          '• <strong>Club (User):</strong> For news manually posted by registered clubs'
        }),
        ('Dates', {
            'fields': ('published_date', 'created_at')
        }),
    )

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'club_link', 'target_position', 'status_badge', 'published_date']
    list_filter = ['is_open', 'published_date', 'source__league_level', 'club__league_level', 'source', 'club']
    search_fields = ['title', 'description', 'target_position', 'source__name', 'club__club_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
    ordering = ['-published_date']
    actions = ['mark_as_open', 'mark_as_closed']
    
    def club_link(self, obj):
        club_name = obj.get_club_name()
        if obj.source:
            return format_html(
                '<a href="/admin/users/clubsource/{}/change/">{}</a> <span style="color: #3b82f6;">(RSS)</span>',
                obj.source.id, club_name
            )
        elif obj.club:
            return format_html(
                '<a href="/admin/users/clubprofile/{}/change/">{}</a> <span style="color: #10b981;">(User)</span>',
                obj.club.id, club_name
            )
        return club_name
    club_link.short_description = 'Club'
    
    def status_badge(self, obj):
        if obj.is_open:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">OPEN</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">CLOSED</span>'
        )
    status_badge.short_description = 'Status'
    
    def mark_as_open(self, request, queryset):
        updated = queryset.update(is_open=True)
        self.message_user(request, f"{updated} opportunity/opportunities marked as open.")
    mark_as_open.short_description = "Mark selected as OPEN"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(is_open=False)
        self.message_user(request, f"{updated} opportunity/opportunities marked as closed.")
    mark_as_closed.short_description = "Mark selected as CLOSED"
    
    fieldsets = (
        ('Opportunity Information', {
            'fields': ('title', 'link', 'description')
        }),
        ('Source Selection', {
            'fields': ('source', 'club'),
            'description': '<strong>Choose ONE source:</strong><br>'
                          '• <strong>Source (RSS):</strong> For opportunities automatically fetched from RSS feeds<br>'
                          '• <strong>Club (User):</strong> For opportunities manually posted by registered clubs'
        }),
        ('Trial Details', {
            'fields': ('target_position', 'is_open')
        }),
        ('Dates', {
            'fields': ('published_date', 'created_at')
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_type', 'caption_preview', 'total_likes', 'created_at']
    list_filter = ['post_type', 'created_at', 'user__role']
    date_hierarchy = 'created_at'
    search_fields = ['user__username', 'caption', 'award_title']
    readonly_fields = ['created_at', 'updated_at', 'total_likes']
    filter_horizontal = ['likes']
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'post_type')
        }),
        ('Content', {
            'fields': ('caption',)
        }),
        ('Media', {
            'fields': ('image', 'video', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Achievement Stats', {
            'fields': ('goals', 'assists', 'clean_sheets', 'minutes_played', 'match_rating'),
            'classes': ('collapse',),
            'description': 'Fill in relevant stats for player achievements'
        }),
        ('Match Details', {
            'fields': ('match_opponent', 'match_result', 'match_date', 'competition'),
            'classes': ('collapse',)
        }),
        ('Award/Milestone', {
            'fields': ('award_title', 'award_description'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('likes', 'total_likes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'body_preview', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    search_fields = ['user__username', 'body', 'post__caption']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'post']

    def body_preview(self, obj):
        return obj.body[:80] + '...' if len(obj.body) > 80 else obj.body
    body_preview.short_description = 'Comment'


# ---------------------------------------------------------------------------
# Scout Verification Admin
# ---------------------------------------------------------------------------

def _notify(user, message):
    """Helper: create an unread Notification for a user."""
    Notification.objects.create(user=user, message=message)


@admin.register(ScoutVerification)
class ScoutVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'scout_name', 'requested_tier', 'awarded_tier',
        'qualification_body', 'qualification_level',
        'status_badge', 'submitted_at', 'reviewed_at', 'verified_by',
    ]
    list_filter = ['status', 'requested_tier', 'awarded_tier', 'qualification_body']
    search_fields = [
        'scout__user__username', 'scout__user__email',
        'scout__organization', 'qualification_body',
    ]
    ordering = ['-submitted_at']
    readonly_fields = [
        'submitted_at', 'reviewed_at', 'verified_by',
        'verification_checklist_display',
        'certificate_preview', 'dashboard_preview',
        'safeguarding_preview', 'affiliation_preview', 'report_preview',
    ]
    actions = [
        'approve_tier1', 'approve_tier2', 'approve_tier3',
        'flag_submission', 'reject_submission',
    ]

    fieldsets = (
        ('Scout Details', {
            'fields': ('scout',),
        }),
        ('Qualification Details', {
            'fields': (
                'requested_tier', 'awarded_tier',
                'qualification_body', 'qualification_level',
                'fa_fan_number',
            ),
        }),
        ('Document Uploads', {
            'fields': (
                'certificate_file', 'certificate_preview',
                'dashboard_screenshot', 'dashboard_preview',
                'safeguarding_certificate', 'safeguarding_preview',
                'dbs_expiry_date',
                'club_affiliation_proof', 'affiliation_preview',
                'sample_scout_report', 'report_preview',
            ),
        }),
        ('Review Decision', {
            'fields': ('status', 'rejection_reason', 'reviewed_at', 'verified_by'),
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'verification_checklist_display'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',),
        }),
    )

    # ------------------------------------------------------------------
    # List-display helpers
    # ------------------------------------------------------------------

    def scout_name(self, obj):
        return obj.scout.user.get_full_name() or obj.scout.user.username
    scout_name.short_description = 'Scout'

    def status_badge(self, obj):
        colours = {
            'PENDING':  ('#f59e0b', '#fff'),
            'APPROVED': ('#16a34a', '#fff'),
            'REJECTED': ('#dc2626', '#fff'),
            'FLAGGED':  ('#7c3aed', '#fff'),
        }
        bg, fg = colours.get(obj.status, ('#6b7280', '#fff'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:4px;'
            'font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    # ------------------------------------------------------------------
    # Document preview helpers
    # ------------------------------------------------------------------

    def _file_link(self, field_file, label):
        if field_file:
            return format_html(
                '<a href="{}" target="_blank" style="color:#2563eb;">&#128196; {}</a>',
                field_file.url, label
            )
        return '—'

    def _image_preview(self, field_file, label):
        if field_file:
            try:
                return format_html(
                    '<a href="{url}" target="_blank">'
                    '<img src="{url}" style="max-height:120px;max-width:240px;border:1px solid #e5e7eb;border-radius:4px;">'
                    '</a>',
                    url=field_file.url
                )
            except Exception:
                return self._file_link(field_file, label)
        return '—'

    def certificate_preview(self, obj):
        return self._file_link(obj.certificate_file, 'View Certificate')
    certificate_preview.short_description = 'Certificate'

    def dashboard_preview(self, obj):
        return self._image_preview(obj.dashboard_screenshot, 'Dashboard Screenshot')
    dashboard_preview.short_description = 'Dashboard Screenshot'

    def safeguarding_preview(self, obj):
        return self._file_link(obj.safeguarding_certificate, 'View Safeguarding Certificate')
    safeguarding_preview.short_description = 'Safeguarding Certificate'

    def affiliation_preview(self, obj):
        return self._file_link(obj.club_affiliation_proof, 'View Affiliation Proof')
    affiliation_preview.short_description = 'Affiliation Proof'

    def report_preview(self, obj):
        return self._file_link(obj.sample_scout_report, 'View Sample Report')
    report_preview.short_description = 'Sample Scout Report'

    # ------------------------------------------------------------------
    # Checklist readonly display
    # ------------------------------------------------------------------

    def verification_checklist_display(self, obj):
        tier_label = obj.get_requested_tier_display() or 'N/A'
        body_label = obj.get_qualification_body_display() if obj.qualification_body else 'N/A'
        items = [
            ('Requested Tier', tier_label),
            ('Qualification Body', body_label),
            ('Qualification Level', obj.get_qualification_level_display() if obj.qualification_level else 'N/A'),
            ('FAN Number Provided', 'Yes' if obj.fa_fan_number else 'No'),
            ('Certificate Uploaded', 'Yes' if obj.certificate_file else 'No'),
            ('Dashboard Screenshot', 'Yes' if obj.dashboard_screenshot else 'No'),
            ('Safeguarding Certificate', 'Yes' if obj.safeguarding_certificate else 'No'),
            ('DBS Expiry Date', str(obj.dbs_expiry_date) if obj.dbs_expiry_date else 'Not provided'),
            ('Club Affiliation Proof', 'Yes' if obj.club_affiliation_proof else 'No'),
            ('Sample Scout Report', 'Yes' if obj.sample_scout_report else 'No'),
        ]
        rows = ''.join(
            f'<tr><td style="padding:4px 12px 4px 0;font-weight:600;">{k}</td>'
            f'<td style="padding:4px 0;">{v}</td></tr>'
            for k, v in items
        )
        return format_html('<table style="font-size:13px;">{}</table>', rows)
    verification_checklist_display.short_description = 'Verification Checklist'

    # ------------------------------------------------------------------
    # Bulk actions
    # ------------------------------------------------------------------

    def _approve(self, request, queryset, tier):
        tier_label = dict(ScoutVerification.TIER_CHOICES).get(tier, tier)
        count = 0
        for verification in queryset.select_related('scout__user'):
            if verification.status in ('PENDING', 'FLAGGED'):
                verification.status = 'APPROVED'
                verification.awarded_tier = tier
                verification.reviewed_at = timezone.now()
                verification.verified_by = request.user
                verification.save()
                # Update ScoutProfile
                sp = verification.scout
                sp.scout_verified = True
                sp.verification_tier = tier
                sp.save()
                # Notify scout
                _notify(
                    sp.user,
                    f'Congratulations! Your scout verification has been approved at '
                    f'{tier_label} level.'
                )
                count += 1
        self.message_user(request, f'{count} scout(s) approved at {tier_label}.')

    def approve_tier1(self, request, queryset):
        self._approve(request, queryset, 'TIER1')
    approve_tier1.short_description = 'Approve selected as Tier 1 (Grassroots)'

    def approve_tier2(self, request, queryset):
        self._approve(request, queryset, 'TIER2')
    approve_tier2.short_description = 'Approve selected as Tier 2 (Semi-Professional)'

    def approve_tier3(self, request, queryset):
        self._approve(request, queryset, 'TIER3')
    approve_tier3.short_description = 'Approve selected as Tier 3 (Professional)'

    def flag_submission(self, request, queryset):
        count = 0
        for verification in queryset.select_related('scout__user'):
            if verification.status == 'PENDING':
                verification.status = 'FLAGGED'
                verification.reviewed_at = timezone.now()
                verification.verified_by = request.user
                verification.save()
                _notify(
                    verification.scout.user,
                    'Your scout verification submission has been flagged for further review. '
                    'An administrator may contact you for additional information.'
                )
                count += 1
        self.message_user(request, f'{count} submission(s) flagged for review.')
    flag_submission.short_description = 'Flag selected submissions for further review'

    def reject_submission(self, request, queryset):
        count = 0
        for verification in queryset.select_related('scout__user'):
            if verification.status in ('PENDING', 'FLAGGED'):
                verification.status = 'REJECTED'
                verification.reviewed_at = timezone.now()
                verification.verified_by = request.user
                verification.save()
                # Revoke ScoutProfile verified status
                sp = verification.scout
                sp.scout_verified = False
                sp.verification_tier = None
                sp.save()
                _notify(
                    sp.user,
                    'Your scout verification application has been rejected. '
                    'Please review the rejection reason in your verification status page '
                    'and resubmit if you have the correct documentation.'
                )
                count += 1
        self.message_user(request, f'{count} submission(s) rejected.')
    reject_submission.short_description = 'Reject selected submissions'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__username', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message'


# ===================================================================
# Follow System Admin
# ===================================================================

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']
    raw_id_fields = ['follower', 'following']


@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['from_user', 'to_user']


# ===================================================================
# Messaging Admin
# ===================================================================

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant_names', 'message_count', 'created_at', 'updated_at']
    search_fields = ['participants__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']

    def participant_names(self, obj):
        return ', '.join(obj.participants.values_list('username', flat=True))
    participant_names.short_description = 'Participants'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'body_preview', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['sender__username', 'body']
    readonly_fields = ['sent_at']
    raw_id_fields = ['sender', 'conversation']

    def body_preview(self, obj):
        return obj.body[:60] + '...' if len(obj.body) > 60 else obj.body
    body_preview.short_description = 'Message'


# ===================================================================
# Fan Profile Admin
# ===================================================================

@admin.register(FanProfile)
class FanProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'favourite_club', 'location', 'created_at']
    search_fields = ['user__username', 'favourite_club', 'location']
    readonly_fields = ['created_at']


# ===================================================================
# Watchlist / Shortlist Admin
# ===================================================================

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['scout_name', 'player_name', 'added_at']
    list_filter = ['added_at']
    search_fields = ['scout__user__username', 'player__user__username']
    readonly_fields = ['added_at']
    raw_id_fields = ['scout', 'player']

    def scout_name(self, obj):
        return obj.scout.user.username
    scout_name.short_description = 'Scout'

    def player_name(self, obj):
        return obj.player.user.username
    player_name.short_description = 'Player'


@admin.register(ClubShortlist)
class ClubShortlistAdmin(admin.ModelAdmin):
    list_display = ['club_name', 'player_name', 'opportunity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['club__club_name', 'player__user__username']
    readonly_fields = ['added_at']
    raw_id_fields = ['club', 'player', 'opportunity']

    def club_name(self, obj):
        return obj.club.club_name
    club_name.short_description = 'Club'

    def player_name(self, obj):
        return obj.player.user.username
    player_name.short_description = 'Player'


# ===================================================================
# Contact Submissions Admin
# ===================================================================

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'category', 'subject', 'message', 'user', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 30

    fieldsets = (
        ('Submission Details', {
            'fields': ('name', 'email', 'user', 'category', 'subject', 'message', 'created_at'),
        }),
        ('Admin Response', {
            'fields': ('status', 'admin_notes'),
            'description': 'Update the status and add internal notes as you handle this submission.',
        }),
    )


# ===================================================================
# Report System Admin (Community Moderation)
# ===================================================================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin interface for managing user reports and community moderation.

    SINGLE-ADMIN WORKFLOW:
    1. Reports appear in 'Pending Review' status
    2. Review the reported content using preview links
    3. Take appropriate action (warning, removal, suspension)
    4. Update status to 'Action Taken' or 'Dismissed'

    PRIORITY LEVELS:
    - Critical (4): Violence, hate speech - requires immediate attention
    - High (3): Harassment, scams, doxxing
    - Medium (2): Inappropriate content, fake accounts
    - Low (1): Spam, minor violations
    """
    list_display = [
        'id', 'status_badge', 'priority_badge', 'reason_display',
        'content_type', 'reporter_name', 'reported_user_name',
        'created_at', 'action_taken_badge'
    ]
    list_filter = ['status', 'priority', 'reason', 'content_type', 'action_taken', 'created_at']
    search_fields = [
        'reporter__username', 'reported_user__username',
        'description', 'admin_notes'
    ]
    ordering = ['-priority', '-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = [
        'reporter', 'content_type', 'reported_user', 'reported_post', 'reported_comment',
        'reason', 'description', 'screenshot', 'created_at', 'updated_at',
        'content_preview_display', 'reporter_history_display', 'reported_user_history_display'
    ]

    actions = [
        'mark_under_review', 'dismiss_no_violation', 'dismiss_duplicate',
        'issue_warning', 'remove_content',
        'suspend_24h', 'suspend_7d', 'suspend_30d', 'ban_user'
    ]

    fieldsets = (
        ('Quick Actions Guide', {
            'fields': (),
            'description': '<div style="background:#f0fdf4;border:2px solid #22c55e;padding:16px;border-radius:8px;margin-bottom:12px;">'
                          '<strong style="color:#166534;font-size:14px;">SINGLE-ADMIN MODERATION WORKFLOW</strong><br><br>'
                          '<strong>Step 1:</strong> Review the reported content below<br>'
                          '<strong>Step 2:</strong> Check user history (warnings, previous reports)<br>'
                          '<strong>Step 3:</strong> Decide on action using bulk actions or manual selection<br>'
                          '<strong>Step 4:</strong> Add notes and update status<br><br>'
                          '<strong style="color:#dc2626;">Priority Guide:</strong> Critical/High = same-day response, Medium = 48 hours, Low = 1 week'
                          '</div>'
        }),
        ('Report Details', {
            'fields': ('reporter', 'content_type', 'reason', 'description', 'screenshot', 'created_at'),
        }),
        ('Reported Content', {
            'fields': ('reported_user', 'reported_post', 'reported_comment', 'content_preview_display'),
            'description': 'View the specific content that was reported.'
        }),
        ('User History (Important)', {
            'fields': ('reporter_history_display', 'reported_user_history_display'),
            'description': 'Check if these users have a history of reports.'
        }),
        ('Admin Decision', {
            'fields': ('status', 'priority', 'action_taken', 'admin_notes', 'resolution_notes', 'reviewed_by', 'reviewed_at'),
            'description': '<strong>admin_notes</strong> = Internal only (reporter cannot see)<br>'
                          '<strong>resolution_notes</strong> = Summary sent to reporter (optional)'
        }),
    )

    # ----------------------------------------------------------------
    # Display helpers
    # ----------------------------------------------------------------

    def reporter_name(self, obj):
        if obj.reporter:
            return obj.reporter.username
        return 'Deleted User'
    reporter_name.short_description = 'Reporter'

    def reported_user_name(self, obj):
        if obj.reported_user:
            return format_html(
                '<a href="/admin/users/user/{}/change/" style="color:#2563eb;">{}</a>',
                obj.reported_user.id, obj.reported_user.username
            )
        return '-'
    reported_user_name.short_description = 'Reported User'

    def status_badge(self, obj):
        colours = {
            'PENDING': ('#f59e0b', '#fffbeb', '⏳'),
            'UNDER_REVIEW': ('#3b82f6', '#eff6ff', '🔍'),
            'ACTION_TAKEN': ('#059669', '#ecfdf5', '✅'),
            'DISMISSED': ('#6b7280', '#f9fafb', '✗'),
            'DUPLICATE': ('#8b5cf6', '#f5f3ff', '📋'),
        }
        bg, bg_light, icon = colours.get(obj.status, ('#6b7280', '#f9fafb', '❓'))
        return format_html(
            '<span style="background:{};color:{};padding:4px 10px;border-radius:12px;font-size:11px;font-weight:bold;">'
            '{} {}</span>',
            bg_light, bg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def priority_badge(self, obj):
        colours = {
            1: ('#22c55e', 'Low'),
            2: ('#f59e0b', 'Med'),
            3: ('#ef4444', 'High'),
            4: ('#7c2d12', 'CRIT'),
        }
        bg, label = colours.get(obj.priority, ('#6b7280', '?'))
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;">{}</span>',
            bg, label
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'

    def reason_display(self, obj):
        return obj.get_reason_display()
    reason_display.short_description = 'Reason'

    def action_taken_badge(self, obj):
        if obj.action_taken == 'NONE':
            return '-'
        colours = {
            'WARNING': '#f59e0b',
            'CONTENT_REMOVED': '#3b82f6',
            'SUSPENDED_24H': '#f97316',
            'SUSPENDED_7D': '#ef4444',
            'SUSPENDED_30D': '#dc2626',
            'BANNED': '#7c2d12',
        }
        bg = colours.get(obj.action_taken, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:10px;">{}</span>',
            bg, obj.get_action_taken_display()
        )
    action_taken_badge.short_description = 'Action'

    def content_preview_display(self, obj):
        preview = obj.get_reported_content_preview()
        if obj.content_type == 'POST' and obj.reported_post:
            return format_html(
                '<div style="background:#f9fafb;padding:12px;border-radius:8px;border:1px solid #e5e7eb;">'
                '<strong>Post Content:</strong><br>{}<br><br>'
                '<a href="/admin/users/post/{}/change/" target="_blank" style="color:#2563eb;">View Full Post in Admin</a>'
                '</div>',
                preview, obj.reported_post.id
            )
        elif obj.content_type == 'COMMENT' and obj.reported_comment:
            return format_html(
                '<div style="background:#f9fafb;padding:12px;border-radius:8px;border:1px solid #e5e7eb;">'
                '<strong>Comment:</strong><br>{}<br><br>'
                '<a href="/admin/users/comment/{}/change/" target="_blank" style="color:#2563eb;">View Comment in Admin</a>'
                '</div>',
                preview, obj.reported_comment.id
            )
        return format_html(
            '<div style="background:#f9fafb;padding:12px;border-radius:8px;border:1px solid #e5e7eb;">{}</div>',
            preview
        )
    content_preview_display.short_description = 'Content Preview'

    def reporter_history_display(self, obj):
        if not obj.reporter:
            return 'Reporter account deleted'
        reports_made = Report.objects.filter(reporter=obj.reporter).count()
        false_reports = Report.objects.filter(reporter=obj.reporter, status='DISMISSED').count()
        return format_html(
            '<div style="font-size:12px;">'
            '<strong>Total reports submitted:</strong> {}<br>'
            '<strong>Dismissed (false reports):</strong> {}<br>'
            '{}'
            '</div>',
            reports_made,
            false_reports,
            '<span style="color:#dc2626;">⚠️ Frequent false reporter</span>' if false_reports >= 3 else ''
        )
    reporter_history_display.short_description = 'Reporter History'

    def reported_user_history_display(self, obj):
        if not obj.reported_user:
            return 'No user specified or account deleted'
        reports_against = Report.objects.filter(reported_user=obj.reported_user).count()
        action_reports = Report.objects.filter(
            reported_user=obj.reported_user,
            status='ACTION_TAKEN'
        ).count()
        warnings = obj.reported_user.warning_count
        is_suspended = obj.reported_user.is_suspended

        status_html = ''
        if is_suspended:
            status_html = '<span style="color:#dc2626;font-weight:bold;">🚫 CURRENTLY SUSPENDED</span><br>'

        return format_html(
            '<div style="font-size:12px;">'
            '{}'
            '<strong>Total reports against:</strong> {}<br>'
            '<strong>Reports with action taken:</strong> {}<br>'
            '<strong>Warning count:</strong> {}<br>'
            '</div>',
            status_html,
            reports_against,
            action_reports,
            warnings
        )
    reported_user_history_display.short_description = 'Reported User History'

    # ----------------------------------------------------------------
    # Bulk Actions
    # ----------------------------------------------------------------

    def mark_under_review(self, request, queryset):
        queryset.update(
            status='UNDER_REVIEW',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'🔍 {queryset.count()} report(s) marked as Under Review.')
    mark_under_review.short_description = '🔍 Mark as Under Review'

    def dismiss_no_violation(self, request, queryset):
        queryset.update(
            status='DISMISSED',
            action_taken='NONE',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'✗ {queryset.count()} report(s) dismissed - no violation found.')
    dismiss_no_violation.short_description = '✗ Dismiss - No Violation'

    def dismiss_duplicate(self, request, queryset):
        queryset.update(
            status='DUPLICATE',
            action_taken='NONE',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'📋 {queryset.count()} report(s) marked as duplicates.')
    dismiss_duplicate.short_description = '📋 Dismiss - Duplicate'

    def issue_warning(self, request, queryset):
        count = 0
        for report in queryset.select_related('reported_user'):
            if report.reported_user:
                report.reported_user.warning_count += 1
                report.reported_user.save(update_fields=['warning_count'])
                # Create notification for the warned user
                Notification.objects.create(
                    user=report.reported_user,
                    message=f'You have received a warning for violating our Community Guidelines. '
                            f'Reason: {report.get_reason_display()}. '
                            f'Further violations may result in account suspension.'
                )
            report.status = 'ACTION_TAKEN'
            report.action_taken = 'WARNING'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            count += 1
        self.message_user(request, f'⚠️ {count} warning(s) issued to users.')
    issue_warning.short_description = '⚠️ Issue Warning'

    def remove_content(self, request, queryset):
        count = 0
        for report in queryset:
            if report.reported_post:
                report.reported_post.delete()
            elif report.reported_comment:
                report.reported_comment.delete()
            report.status = 'ACTION_TAKEN'
            report.action_taken = 'CONTENT_REMOVED'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            count += 1
        self.message_user(request, f'🗑️ Content removed for {count} report(s).')
    remove_content.short_description = '🗑️ Remove Reported Content'

    def _suspend_user(self, request, queryset, days, action_code):
        from datetime import timedelta
        count = 0
        for report in queryset.select_related('reported_user'):
            if report.reported_user:
                report.reported_user.is_suspended = True
                report.reported_user.suspension_end_date = timezone.now() + timedelta(days=days)
                report.reported_user.suspension_reason = f'Suspended for {report.get_reason_display()}'
                report.reported_user.save(update_fields=['is_suspended', 'suspension_end_date', 'suspension_reason'])
                Notification.objects.create(
                    user=report.reported_user,
                    message=f'Your account has been suspended for {days} days due to a violation of our '
                            f'Community Guidelines. Reason: {report.get_reason_display()}.'
                )
            report.status = 'ACTION_TAKEN'
            report.action_taken = action_code
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            count += 1
        return count

    def suspend_24h(self, request, queryset):
        count = self._suspend_user(request, queryset, 1, 'SUSPENDED_24H')
        self.message_user(request, f'🚫 {count} user(s) suspended for 24 hours.')
    suspend_24h.short_description = '🚫 Suspend User (24 Hours)'

    def suspend_7d(self, request, queryset):
        count = self._suspend_user(request, queryset, 7, 'SUSPENDED_7D')
        self.message_user(request, f'🚫 {count} user(s) suspended for 7 days.')
    suspend_7d.short_description = '🚫 Suspend User (7 Days)'

    def suspend_30d(self, request, queryset):
        count = self._suspend_user(request, queryset, 30, 'SUSPENDED_30D')
        self.message_user(request, f'🚫 {count} user(s) suspended for 30 days.')
    suspend_30d.short_description = '🚫 Suspend User (30 Days)'

    def ban_user(self, request, queryset):
        count = 0
        for report in queryset.select_related('reported_user'):
            if report.reported_user:
                report.reported_user.is_active = False
                report.reported_user.is_suspended = True
                report.reported_user.suspension_reason = f'Permanently banned for {report.get_reason_display()}'
                report.reported_user.save(update_fields=['is_active', 'is_suspended', 'suspension_reason'])
            report.status = 'ACTION_TAKEN'
            report.action_taken = 'BANNED'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            count += 1
        self.message_user(request, f'⛔ {count} user(s) permanently banned.')
    ban_user.short_description = '⛔ Permanently Ban User'
