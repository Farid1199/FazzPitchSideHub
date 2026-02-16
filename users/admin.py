from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile, 
    ManagerProfile, QualificationVerification, ClubSource, NewsItem, Opportunity, Post
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
    list_display = ['manager_name', 'qualification_type', 'status', 'submitted_at', 'view_certificate', 'action_buttons']
    list_filter = ['status', 'qualification_type', 'submitted_at']
    search_fields = ['manager__user__username', 'fa_fan_number']
    readonly_fields = ['manager', 'submitted_at', 'certificate_preview']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Verification Request', {
            'fields': ('manager', 'qualification_type', 'status', 'submitted_at')
        }),
        ('Certificate Information', {
            'fields': ('certificate_preview', 'fa_fan_number')
        }),
        ('Admin Review', {
            'fields': ('admin_notes', 'reviewed_at')
        }),
    )
    
    actions = ['approve_verification', 'reject_verification']
    
    def manager_name(self, obj):
        return obj.manager.user.username
    manager_name.short_description = 'Manager'
    
    def view_certificate(self, obj):
        if obj.certificate_image:
            return format_html('<a href="{}" target="_blank">View Certificate</a>', obj.certificate_image.url)
        return "No certificate"
    view_certificate.short_description = 'Certificate'
    
    def certificate_preview(self, obj):
        if obj.certificate_image:
            return format_html('<img src="{}" style="max-width: 500px; max-height: 500px;"/>', obj.certificate_image.url)
        return "No certificate uploaded"
    certificate_preview.short_description = 'Certificate Image'
    
    def action_buttons(self, obj):
        if obj.status == 'PENDING':
            return format_html(
                '<a class="button" href="/admin/users/qualificationverification/{}/change/">Review</a>',
                obj.pk
            )
        return obj.status
    action_buttons.short_description = 'Actions'
    
    def approve_verification(self, request, queryset):
        for verification in queryset:
            verification.status = 'APPROVED'
            verification.reviewed_at = timezone.now()
            verification.save()
            # Update the manager's profile
            manager = verification.manager
            manager.qualification_verified = True
            manager.save()
        self.message_user(request, f"{queryset.count()} verification(s) approved.")
    approve_verification.short_description = "Approve selected verifications"
    
    def reject_verification(self, request, queryset):
        for verification in queryset:
            verification.status = 'REJECTED'
            verification.reviewed_at = timezone.now()
            verification.save()
        self.message_user(request, f"{queryset.count()} verification(s) rejected.")
    reject_verification.short_description = "Reject selected verifications"


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
