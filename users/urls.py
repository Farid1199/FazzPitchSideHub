from django.urls import path
from .views import (
    # Authentication
    register_view, login_view, logout_view, dashboard_view,
    
    # Public views
    home_view, public_profile_view, public_players_list, 
    public_clubs_list, public_trials_list, feed_view,
    
    # Profile management
    profile_edit_view,
    
    # Trial management
    create_trial_view, my_trials_view, trial_detail_view, apply_trial_view,
    
    # Messaging
    messages_list_view, send_message_view, message_detail_view,
    
    # Media
    upload_media_view, my_media_view,
    
    # Endorsements
    endorse_user_view,
    
    # Notifications
    notifications_view,
    
    # Legacy views
    players_list_view, clubs_list_view, coaches_list_view,
    scouts_list_view, volunteers_list_view
)

urlpatterns = [
    # Authentication
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Public views (no login required)
    path('players/', public_players_list, name='public_players_list'),
    path('clubs/', public_clubs_list, name='public_clubs_list'),
    path('trials/', public_trials_list, name='public_trials_list'),
    path('feed/', feed_view, name='feed'),
    path('profile/<str:username>/', public_profile_view, name='public_profile'),
    
    # Profile management
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    
    # Trial management
    path('trials/create/', create_trial_view, name='create_trial'),
    path('trials/my/', my_trials_view, name='my_trials'),
    path('trials/<int:trial_id>/', trial_detail_view, name='trial_detail'),
    path('trials/<int:trial_id>/apply/', apply_trial_view, name='apply_trial'),
    
    # Messaging system
    path('messages/', messages_list_view, name='messages_list'),
    path('messages/send/', send_message_view, name='send_message'),
    path('messages/send/<str:username>/', send_message_view, name='send_message_to'),
    path('messages/<int:message_id>/', message_detail_view, name='message_detail'),
    
    # Media management
    path('media/upload/', upload_media_view, name='upload_media'),
    path('media/my/', my_media_view, name='my_media'),
    
    # Endorsements
    path('endorse/<str:username>/', endorse_user_view, name='endorse_user'),
    
    # Notifications
    path('notifications/', notifications_view, name='notifications'),
    
    # Legacy URLs for compatibility
    path('players-list/', players_list_view, name='players-list'),
    path('clubs-list/', clubs_list_view, name='clubs-list'),
    path('coaches/', coaches_list_view, name='coaches-list'),
    path('scouts/', scouts_list_view, name='scouts-list'),
    path('volunteers/', volunteers_list_view, name='volunteers-list'),
]