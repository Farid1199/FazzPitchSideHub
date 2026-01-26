from django.contrib import admin
from .models import User, PlayerProfile, ClubProfile, ScoutProfile, NewsItem, Opportunity

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
