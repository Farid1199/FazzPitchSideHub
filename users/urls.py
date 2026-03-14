from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    signup_view, login_view, select_role,
    player_setup, club_setup, scout_setup, manager_setup, fan_setup,
    role_selection_view, profile_creation_view, 
    dashboard_view, home_view, feeds_view, search_players, search_clubs,
    edit_profile, submit_qualification_verification, post_opportunity,
    opportunity_detail, express_interest, withdraw_interest, verify_opportunity,
    news_detail, player_profile, community_hub,
    create_post, social_feed, like_post, delete_post, my_posts,
    add_comment, delete_comment,
    submit_scout_verification, scout_verification_status, protected_scout_media,
    protected_manager_media,
    # Part 3 – Follow
    follow_user, unfollow_user, accept_follow_request, reject_follow_request,
    followers_list, following_list,
    # Part 4 – Messaging
    inbox_view, conversation_view, start_conversation, get_new_messages, get_unread_count,
    # Part 5 – Notifications
    notifications_view, get_notification_count, get_notifications_dropdown,
    # Part 7 – Watchlist / Shortlist
    add_to_watchlist, remove_from_watchlist, scout_watchlist_view, update_watchlist_notes,
    add_to_shortlist, remove_from_shortlist, club_shortlist_view,
    # Part 9 – AI Bio
    generate_bio_view,
    # Part 12 – Security / GDPR
    delete_account_view, privacy_policy, about_page, contact_page, security_settings,
    verify_email_view, resend_verification_email, export_data_view,
    # Part 13 – Football Pathways
    pathways_home, pathways_player, pathways_manager, pathways_scout,
    pathways_non_league, pathways_qualifications,
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
    path('fan-setup/', fan_setup, name='fan_setup'),
    
    # Legacy URLs (keep for backwards compatibility)
    path('role-selection/', role_selection_view, name='role_selection'),
    path('profile-creation/', profile_creation_view, name='profile_creation'),
    
    path('dashboard/', dashboard_view, name='dashboard'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('submit-verification/', submit_qualification_verification, name='submit_verification'),
    
    # Scout Verification
    path('scout-verification/', submit_scout_verification, name='submit_scout_verification'),
    path('scout-verification/status/', scout_verification_status, name='scout_verification_status'),
    path('scout-media/<path:path>', protected_scout_media, name='protected_scout_media'),
    path('manager-media/<path:path>', protected_manager_media, name='protected_manager_media'),
    
    path('post-opportunity/', post_opportunity, name='post_opportunity'),
    path('opportunity/<int:pk>/', opportunity_detail, name='opportunity_detail'),
    path('opportunity/<int:pk>/express-interest/', express_interest, name='express_interest'),
    path('opportunity/<int:pk>/withdraw-interest/', withdraw_interest, name='withdraw_interest'),
    path('opportunity/<int:pk>/verify/', verify_opportunity, name='verify_opportunity'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('player/<str:username>/', player_profile, name='player_profile'),
    path('search-players/', search_players, name='search_players'),
    path('search-clubs/', search_clubs, name='search_clubs'),
    path('feeds/', feeds_view, name='feeds'),
    path('feeds/trial/', feeds_view, {'category': 'trial'}, name='feeds_trial'),
    path('feeds/general/', feeds_view, {'category': 'general'}, name='feeds_general'),
    path('feeds/transfer/', feeds_view, {'category': 'transfer'}, name='feeds_transfer'),
    path('feeds/match/', feeds_view, {'category': 'match'}, name='feeds_match'),
    path('feeds/signals/', feeds_view, {'category': 'recruitment_signal'}, name='feeds_signals'),
    path('community-hub/', community_hub, name='community_hub'),
    
    # Social Media Posts
    path('posts/create/', create_post, name='create_post'),
    path('posts/feed/', social_feed, name='social_feed'),
    path('posts/my-posts/', my_posts, name='my_posts'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('comments/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    
    # Follow System
    path('follow/<int:user_id>/', follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow_user'),
    path('follow-request/<int:request_id>/accept/', accept_follow_request, name='accept_follow_request'),
    path('follow-request/<int:request_id>/reject/', reject_follow_request, name='reject_follow_request'),
    path('user/<int:user_id>/followers/', followers_list, name='followers_list'),
    path('user/<int:user_id>/following/', following_list, name='following_list'),
    
    # Messaging
    path('messages/', inbox_view, name='inbox'),
    path('messages/<int:conversation_id>/', conversation_view, name='conversation'),
    path('messages/start/<int:user_id>/', start_conversation, name='start_conversation'),
    path('messages/<int:conversation_id>/new/', get_new_messages, name='get_new_messages'),
    path('api/unread-count/', get_unread_count, name='get_unread_count'),
    
    # Notifications
    path('notifications/', notifications_view, name='notifications'),
    path('api/notification-count/', get_notification_count, name='get_notification_count'),
    path('api/notifications-dropdown/', get_notifications_dropdown, name='get_notifications_dropdown'),
    
    # Watchlist / Shortlist
    path('watchlist/add/<int:player_id>/', add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:player_id>/', remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', scout_watchlist_view, name='scout_watchlist'),
    path('watchlist/<int:watchlist_id>/notes/', update_watchlist_notes, name='update_watchlist_notes'),
    path('shortlist/add/<int:player_id>/', add_to_shortlist, name='add_to_shortlist'),
    path('shortlist/remove/<int:player_id>/', remove_from_shortlist, name='remove_from_shortlist'),
    path('shortlist/', club_shortlist_view, name='club_shortlist'),
    
    # AI Bio Generator
    path('api/generate-bio/', generate_bio_view, name='generate_bio'),
    
    # Security / GDPR
    path('settings/security/', security_settings, name='security_settings'),
    path('account/delete/', delete_account_view, name='delete_account'),
    path('account/export/', export_data_view, name='export_data'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('verify-email/<str:token>/', verify_email_view, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    # Football Pathways — Educational Hub
    path('pathways/', pathways_home, name='pathways_home'),
    path('pathways/become-player/', pathways_player, name='pathways_player'),
    path('pathways/become-manager/', pathways_manager, name='pathways_manager'),
    path('pathways/become-scout/', pathways_scout, name='pathways_scout'),
    path('pathways/non-league/', pathways_non_league, name='pathways_non_league'),
    path('pathways/qualifications/', pathways_qualifications, name='pathways_qualifications'),

    path('', home_view, name='home'),
]