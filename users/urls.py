from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    signup_view, login_view, select_role,
    player_setup, club_setup, scout_setup,
    role_selection_view, profile_creation_view, 
    dashboard_view, home_view, search_players
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # New role-based onboarding flow
    path('select-role/', select_role, name='select_role'),
    path('player-setup/', player_setup, name='player_setup'),
    path('club-setup/', club_setup, name='club_setup'),
    path('scout-setup/', scout_setup, name='scout_setup'),
    
    # Legacy URLs (keep for backwards compatibility)
    path('role-selection/', role_selection_view, name='role_selection'),
    path('profile-creation/', profile_creation_view, name='profile_creation'),
    
    path('dashboard/', dashboard_view, name='dashboard'),
    path('search-players/', search_players, name='search_players'),
    path('', home_view, name='home'),
]
