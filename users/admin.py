from django.contrib import admin
from .models import CustomUser, PlayerProfile, ClubProfile, ScoutProfile

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_role_selected']
    list_filter = ['user_type', 'is_role_selected']
    search_fields = ['username', 'email']

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'playing_level']
    search_fields = ['user__username', 'position']

@admin.register(ClubProfile)
class ClubProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'club_name', 'league']
    search_fields = ['user__username', 'club_name']

@admin.register(ScoutProfile)
class ScoutProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'region']
    search_fields = ['user__username', 'organization']
