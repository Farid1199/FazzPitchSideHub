from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from .forms import (
    CustomUserCreationForm, CustomLoginForm, ProfileUpdateForm, 
    TrialForm, MessageForm, MediaUploadForm, EndorsementForm, 
    SearchForm, TrialApplicationForm
)
from .models import (
    CustomUser, Trial, Message, Media, Endorsement, 
    Notification, Post, TrialApplication
)

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FazzPitchSideHub, {user.username}!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

# Public Views (No login required)
def home_view(request):
    """Public homepage with latest updates"""
    recent_posts = Post.objects.filter(is_public=True)[:5]
    recent_trials = Trial.objects.filter(is_public=True, date__gte=timezone.now())[:3]
    featured_players = CustomUser.objects.filter(
        user_type='PLAYER', 
        profile_visibility='PUBLIC'
    )[:4]
    
    context = {
        'recent_posts': recent_posts,
        'recent_trials': recent_trials,
        'featured_players': featured_players,
    }
    return render(request, 'users/home.html', context)

def public_profile_view(request, username):
    """Public profile view for any user"""
    user_profile = get_object_or_404(CustomUser, username=username)
    
    # Check visibility permissions
    if user_profile.profile_visibility == 'PRIVATE':
        if not request.user.is_authenticated or request.user != user_profile:
            messages.error(request, 'This profile is private.')
            return redirect('home')
    elif user_profile.profile_visibility == 'VERIFIED_ONLY':
        if not request.user.is_authenticated or (not request.user.is_verified and request.user != user_profile):
            messages.error(request, 'This profile is only visible to verified users.')
            return redirect('home')
    
    # Get user's content
    media_items = user_profile.media.filter(is_public=True)[:6]
    endorsements = user_profile.received_endorsements.filter(is_public=True)[:5]
    
    # Track profile view for notifications
    if request.user.is_authenticated and request.user != user_profile:
        Notification.objects.create(
            user=user_profile,
            notification_type='PROFILE_VIEW',
            title=f'{request.user.username} viewed your profile',
            message=f'{request.user.get_full_name() or request.user.username} ({request.user.get_user_type_display()}) viewed your profile.',
            related_url=reverse('public_profile', kwargs={'username': request.user.username})
        )
    
    context = {
        'profile_user': user_profile,
        'media_items': media_items,
        'endorsements': endorsements,
        'can_endorse': request.user.is_authenticated and request.user != user_profile,
    }
    return render(request, 'users/public_profile.html', context)

def public_players_list(request):
    """Public list of players with search functionality"""
    form = SearchForm(request.GET)
    players = CustomUser.objects.filter(
        user_type='PLAYER',
        profile_visibility='PUBLIC'
    )
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        location = form.cleaned_data.get('location')
        position = form.cleaned_data.get('position')
        verified_only = form.cleaned_data.get('verified_only')
        
        if query:
            players = players.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(bio__icontains=query)
            )
        if location:
            players = players.filter(location__icontains=location)
        if position:
            players = players.filter(position__icontains=position)
        if verified_only:
            players = players.filter(is_verified=True)
    
    paginator = Paginator(players, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'players': page_obj,
        'form': form,
        'total_count': players.count(),
    }
    return render(request, 'users/public_players_list.html', context)

def public_clubs_list(request):
    """Public list of clubs"""
    clubs = CustomUser.objects.filter(
        user_type='CLUB',
        profile_visibility='PUBLIC'
    )
    
    paginator = Paginator(clubs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clubs': page_obj,
    }
    return render(request, 'users/public_clubs_list.html', context)

def public_trials_list(request):
    """Public list of upcoming trials"""
    trials = Trial.objects.filter(
        is_public=True,
        date__gte=timezone.now()
    ).order_by('date')
    
    paginator = Paginator(trials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'trials': page_obj,
    }
    return render(request, 'users/public_trials_list.html', context)

# Dashboard Views (Login required)
@login_required
def dashboard_view(request):
    user = request.user
    
    # Get user-specific dashboard data
    unread_notifications = user.notifications.filter(is_read=False)[:5]
    unread_messages = user.received_messages.filter(is_read=False).count()
    
    # Role-specific dashboard data
    context = {
        'user': user,
        'unread_notifications': unread_notifications,
        'unread_messages_count': unread_messages,
    }
    
    if user.user_type == 'PLAYER':
        context['my_applications'] = user.trial_applications.all()[:5]
        context['suggested_trials'] = Trial.objects.filter(
            is_public=True,
            date__gte=timezone.now()
        )[:3]
        return render(request, 'users/dashboards/player_dashboard.html', context)
    
    elif user.user_type == 'CLUB':
        context['my_trials'] = user.trials.all()[:5]
        context['recent_applications'] = TrialApplication.objects.filter(
            trial__club=user
        )[:5]
        return render(request, 'users/dashboards/club_dashboard.html', context)
    
    elif user.user_type == 'SCOUT':
        context['recent_players'] = CustomUser.objects.filter(
            user_type='PLAYER',
            profile_visibility__in=['PUBLIC', 'VERIFIED_ONLY'] if user.is_verified else ['PUBLIC']
        )[:6]
        return render(request, 'users/dashboards/scout_dashboard.html', context)
    
    elif user.user_type == 'COACH':
        return render(request, 'users/dashboards/coach_dashboard.html', context)
    
    elif user.user_type == 'VOLUNTEER':
        return render(request, 'users/dashboards/volunteer_dashboard.html', context)
    
    return render(request, 'users/dashboards/default_dashboard.html', context)

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})

# Trial Management Views
@login_required
def create_trial_view(request):
    if request.user.user_type != 'CLUB':
        messages.error(request, 'Only clubs can create trials.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TrialForm(request.POST)
        if form.is_valid():
            trial = form.save(commit=False)
            trial.club = request.user
            trial.save()
            
            # Create a post for this trial
            Post.objects.create(
                author=request.user,
                post_type='TRIAL',
                content=f"New trial opportunity: {trial.title}",
                related_trial=trial
            )
            
            messages.success(request, 'Trial created successfully!')
            return redirect('my_trials')
    else:
        form = TrialForm()
    
    return render(request, 'users/create_trial.html', {'form': form})

@login_required
def my_trials_view(request):
    if request.user.user_type != 'CLUB':
        messages.error(request, 'Only clubs can view trials.')
        return redirect('dashboard')
    
    trials = request.user.trials.all()
    return render(request, 'users/my_trials.html', {'trials': trials})

@login_required
def trial_detail_view(request, trial_id):
    trial = get_object_or_404(Trial, id=trial_id)
    
    # Check permissions
    if not trial.is_public and trial.club != request.user:
        messages.error(request, 'You do not have permission to view this trial.')
        return redirect('dashboard')
    
    applications = trial.applications.all()
    user_application = None
    
    if request.user.is_authenticated and request.user.user_type == 'PLAYER':
        user_application = trial.applications.filter(player=request.user).first()
    
    context = {
        'trial': trial,
        'applications': applications if trial.club == request.user else None,
        'user_application': user_application,
        'can_apply': (
            request.user.is_authenticated and 
            request.user.user_type == 'PLAYER' and 
            not user_application and 
            trial.date > timezone.now()
        )
    }
    return render(request, 'users/trial_detail.html', context)

@login_required
def apply_trial_view(request, trial_id):
    if request.user.user_type != 'PLAYER':
        messages.error(request, 'Only players can apply for trials.')
        return redirect('dashboard')
    
    trial = get_object_or_404(Trial, id=trial_id)
    
    # Check if already applied
    if trial.applications.filter(player=request.user).exists():
        messages.warning(request, 'You have already applied for this trial.')
        return redirect('trial_detail', trial_id=trial_id)
    
    if request.method == 'POST':
        form = TrialApplicationForm(request.POST)
        if form.is_valid():
            application = TrialApplication.objects.create(
                trial=trial,
                player=request.user,
                message=form.cleaned_data['message']
            )
            
            # Create notification for club
            Notification.objects.create(
                user=trial.club,
                notification_type='TRIAL_APPLICATION',
                title=f'New trial application from {request.user.username}',
                message=f'{request.user.get_full_name() or request.user.username} applied for your trial: {trial.title}',
                related_url=reverse('trial_detail', kwargs={'trial_id': trial.id})
            )
            
            messages.success(request, 'Your application has been submitted!')
            return redirect('trial_detail', trial_id=trial_id)
    else:
        form = TrialApplicationForm()
    
    return render(request, 'users/apply_trial.html', {'form': form, 'trial': trial})

# Messaging System
@login_required
def messages_list_view(request):
    received_messages = request.user.received_messages.all()[:20]
    sent_messages = request.user.sent_messages.all()[:20]
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'users/messages_list.html', context)

@login_required
def send_message_view(request, username=None):
    recipient = None
    if username:
        recipient = get_object_or_404(CustomUser, username=username)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        recipient_username = request.POST.get('recipient')
        if recipient_username:
            recipient = get_object_or_404(CustomUser, username=recipient_username)
        
        if form.is_valid() and recipient:
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            
            # Create notification
            Notification.objects.create(
                user=recipient,
                notification_type='MESSAGE_RECEIVED',
                title=f'New message from {request.user.username}',
                message=f'Subject: {message.subject}',
                related_url=reverse('message_detail', kwargs={'message_id': message.id})
            )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('messages_list')
    else:
        form = MessageForm()
    
    context = {
        'form': form,
        'recipient': recipient,
    }
    return render(request, 'users/send_message.html', context)

@login_required
def message_detail_view(request, message_id):
    message = get_object_or_404(
        Message, 
        Q(id=message_id) & (Q(sender=request.user) | Q(recipient=request.user))
    )
    
    # Mark as read if recipient is viewing
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'users/message_detail.html', {'message': message})

# Media Management
@login_required
def upload_media_view(request):
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.user = request.user
            media.save()
            
            # Create post for media upload
            Post.objects.create(
                author=request.user,
                post_type='MEDIA',
                content=f"Uploaded new {media.get_media_type_display().lower()}: {media.title}",
                related_media=media
            )
            
            messages.success(request, 'Media uploaded successfully!')
            return redirect('my_media')
    else:
        form = MediaUploadForm()
    
    return render(request, 'users/upload_media.html', {'form': form})

@login_required
def my_media_view(request):
    media_items = request.user.media.all()
    return render(request, 'users/my_media.html', {'media_items': media_items})

# Endorsement System
@login_required
def endorse_user_view(request, username):
    user_to_endorse = get_object_or_404(CustomUser, username=username)
    
    if user_to_endorse == request.user:
        messages.error(request, 'You cannot endorse yourself.')
        return redirect('public_profile', username=username)
    
    # Check if already endorsed
    if Endorsement.objects.filter(endorser=request.user, endorsed=user_to_endorse).exists():
        messages.warning(request, 'You have already endorsed this user.')
        return redirect('public_profile', username=username)
    
    if request.method == 'POST':
        form = EndorsementForm(request.POST)
        if form.is_valid():
            endorsement = form.save(commit=False)
            endorsement.endorser = request.user
            endorsement.endorsed = user_to_endorse
            endorsement.save()
            
            # Create notification
            Notification.objects.create(
                user=user_to_endorse,
                notification_type='ENDORSEMENT',
                title=f'{request.user.username} endorsed you!',
                message=endorsement.message[:100] + '...' if len(endorsement.message) > 100 else endorsement.message,
                related_url=reverse('public_profile', kwargs={'username': user_to_endorse.username})
            )
            
            # Create post
            Post.objects.create(
                author=request.user,
                post_type='ENDORSEMENT',
                content=f"Endorsed {user_to_endorse.get_full_name() or user_to_endorse.username}",
                related_endorsement=endorsement
            )
            
            messages.success(request, f'You have endorsed {user_to_endorse.username}!')
            return redirect('public_profile', username=username)
    else:
        form = EndorsementForm()
    
    context = {
        'form': form,
        'user_to_endorse': user_to_endorse,
    }
    return render(request, 'users/endorse_user.html', context)

# Notification Management
@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()[:20]
    
    # Mark all as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'users/notifications.html', {'notifications': notifications})

# Feed View
def feed_view(request):
    """Public feed of recent activities"""
    posts = Post.objects.filter(is_public=True)[:20]
    return render(request, 'users/feed.html', {'posts': posts})

# Legacy views for compatibility
@login_required
def players_list_view(request):
    return redirect('public_players_list')

@login_required
def clubs_list_view(request):
    return redirect('public_clubs_list')

@login_required
def coaches_list_view(request):
    coaches = CustomUser.objects.filter(user_type='COACH')
    return render(request, 'users/coaches_list.html', {'coaches': coaches})

@login_required
def scouts_list_view(request):
    scouts = CustomUser.objects.filter(user_type='SCOUT')
    return render(request, 'users/scouts_list.html', {'scouts': scouts})

@login_required
def volunteers_list_view(request):
    volunteers = CustomUser.objects.filter(user_type='VOLUNTEER')
    return render(request, 'users/volunteers_list.html', {'volunteers': volunteers})