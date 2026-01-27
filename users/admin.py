from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    User, PlayerProfile, ClubProfile, ScoutProfile, 
    ManagerProfile, QualificationVerification, NewsItem, Opportunity
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
    list_display = ['club_name', 'league_level', 'is_registered', 'rss_feed_url', 'location']
    list_filter = ['league_level', 'is_registered', 'location']
    search_fields = ['club_name', 'league', 'location']
    readonly_fields = ['is_registered']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('club_name', 'league_level', 'league', 'location', 'location_postcode', 'founded_year')
        }),
        ('RSS Feed', {
            'fields': ('rss_feed_url',),
            'description': 'Add RSS feed URL to automatically fetch news and opportunities from this club.'
        }),
        ('User Account', {
            'fields': ('user', 'is_registered'),
            'description': 'Link to user account if club has signed up. Leave blank for admin-added clubs.',
            'classes': ('collapse',)
        }),
    )

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
    list_display = ['title', 'club', 'published_date', 'created_at']
    list_filter = ['published_date', 'club']
    search_fields = ['title', 'description', 'club__club_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'target_position', 'is_open', 'published_date']
    list_filter = ['is_open', 'published_date', 'club']
    search_fields = ['title', 'description', 'target_position', 'club__club_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
