from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    signup_view, login_view, select_role,
    player_setup, club_setup, scout_setup, manager_setup,
    role_selection_view, profile_creation_view, 
    dashboard_view, home_view, feeds_view, search_players, search_clubs,
    edit_profile, submit_qualification_verification, post_opportunity,
    opportunity_detail, news_detail, player_profile, community_hub,
    create_post, social_feed, like_post, delete_post, my_posts
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # New role-based onboarding flow
    path('select-role/', select_role, name='select_role'),
    path('player-setup/', player_setup, name='player_setup'),
    path('club-setup/', club_setup, name='club_setup'),
    path('scout-setup/', scout_setup, name='scout_setup'),
    path('manager-setup/', manager_setup, name='manager_setup'),
    
    # Legacy URLs (keep for backwards compatibility)
    path('role-selection/', role_selection_view, name='role_selection'),
    path('profile-creation/', profile_creation_view, name='profile_creation'),
    
    path('dashboard/', dashboard_view, name='dashboard'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('submit-verification/', submit_qualification_verification, name='submit_verification'),
    path('post-opportunity/', post_opportunity, name='post_opportunity'),
    path('opportunity/<int:pk>/', opportunity_detail, name='opportunity_detail'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('player/<str:username>/', player_profile, name='player_profile'),
    path('search-players/', search_players, name='search_players'),
    path('search-clubs/', search_clubs, name='search_clubs'),
    path('feeds/', feeds_view, name='feeds'),
    path('community-hub/', community_hub, name='community_hub'),
    
    # Social Media Posts
    path('posts/create/', create_post, name='create_post'),
    path('posts/feed/', social_feed, name='social_feed'),
    path('posts/my-posts/', my_posts, name='my_posts'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    
    path('', home_view, name='home'),
]