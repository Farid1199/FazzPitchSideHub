from django.contrib import admin
from .models import (
    CustomUser, Trial, Message, Media, Endorsement, 
    Notification, Post, TrialApplication
)

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'created_at']
    list_filter = ['user_type', 'is_verified', 'profile_visibility']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'location', 'date', 'is_public']
    list_filter = ['is_public', 'date']
    search_fields = ['title', 'club__username', 'location']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['subject', 'sender__username', 'recipient__username']

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'media_type', 'created_at', 'is_public']
    list_filter = ['media_type', 'is_public', 'created_at']
    search_fields = ['title', 'user__username']

@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ['endorser', 'endorsed', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['endorser__username', 'endorsed__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'created_at', 'is_read']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_type', 'created_at', 'is_public']
    list_filter = ['post_type', 'is_public', 'created_at']
    search_fields = ['author__username', 'content']

@admin.register(TrialApplication)
class TrialApplicationAdmin(admin.ModelAdmin):
    list_display = ['player', 'trial', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['player__username', 'trial__title']