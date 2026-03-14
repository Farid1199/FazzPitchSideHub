from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, JsonResponse
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings as django_settings
from itertools import chain
import os
import json
import secrets
import re
from .forms import (
    CustomUserCreationForm, PlayerProfileForm, ClubProfileForm, 
    ScoutProfileForm, ManagerProfileForm, QualificationVerificationForm,
    ScoutVerificationForm, OpportunityForm, PostForm, FanProfileForm
)
from .models import (
    User, NewsItem, Opportunity, PlayerProfile, ClubProfile, ClubSource,
    ScoutProfile, ManagerProfile, QualificationVerification, ScoutVerification,
    Notification, Post, Comment, Follow, FollowRequest, Conversation, Message,
    FanProfile, Watchlist, ClubShortlist
)
from .utils import get_recommendations
from .utils_notifications import create_notification


def _send_verification_email(request, user):
    """Send an email verification link to the user."""
    token = secrets.token_urlsafe(48)
    user.email_verification_token = token
    user.save(update_fields=['email_verification_token'])
    verify_url = request.build_absolute_uri(f'/verify-email/{token}/')
    send_mail(
        subject='Verify your email — Fazz PitchSide Hub',
        message=(
            f'Hi {user.username},\n\n'
            f'Please verify your email address by clicking the link below:\n\n'
            f'{verify_url}\n\n'
            f'If you did not create an account, please ignore this email.\n\n'
            f'— Fazz PitchSide Hub'
        ),
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
        fail_silently=True,
    )


def verify_email_view(request, token):
    """Verify a user's email address via the token link."""
    try:
        user = User.objects.get(email_verification_token=token)
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('home')

    if user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
    else:
        user.is_email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['is_email_verified', 'email_verification_token'])
        messages.success(request, 'Your email has been verified successfully!')

    return redirect('dashboard')


@login_required
def resend_verification_email(request):
    """Resend the email verification link."""
    if request.user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
    else:
        _send_verification_email(request, request.user)
        messages.success(request, 'A new verification email has been sent.')
    return redirect('security_settings')

def signup_view(request):
    """
    Handles user registration.
    Redirects to role selection after successful signup.
    Sends email verification link.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.privacy_consent = True
            user.privacy_consent_date = timezone.now()
            user.save()
            # Send email verification
            _send_verification_email(request, user)
            login(request, user)
            messages.info(request, 'A verification link has been sent to your email address. Please verify your email.')
            return redirect('select_role')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


def select_role(request):
    """
    Role selection page - user chooses between Player, Club, Scout, or Manager.
    """
    # If user already has a role, redirect to appropriate setup or dashboard
    if request.user.is_authenticated:
        if request.user.role:
            # Check if they have completed their profile
            if request.user.role == 'PLAYER' and hasattr(request.user, 'player_profile'):
                return redirect('dashboard')
            elif request.user.role == 'CLUB' and hasattr(request.user, 'club_profile'):
                return redirect('dashboard')
            elif request.user.role == 'SCOUT' and hasattr(request.user, 'scout_profile'):
                return redirect('dashboard')
            elif request.user.role == 'MANAGER' and hasattr(request.user, 'manager_profile'):
                return redirect('dashboard')
            elif request.user.role == 'FAN' and hasattr(request.user, 'fan_profile'):
                return redirect('dashboard')
            # If role set but no profile, redirect to appropriate setup
            else:
                if request.user.role == 'PLAYER':
                    return redirect('player_setup')
                elif request.user.role == 'CLUB':
                    return redirect('club_setup')
                elif request.user.role == 'SCOUT':
                    return redirect('scout_setup')
                elif request.user.role == 'MANAGER':
                    return redirect('manager_setup')
                elif request.user.role == 'FAN':
                    return redirect('fan_setup')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['PLAYER', 'CLUB', 'SCOUT', 'MANAGER', 'FAN']:
            request.user.role = role
            request.user.save()
            
            # Redirect to appropriate setup page
            if role == 'PLAYER':
                return redirect('player_setup')
            elif role == 'CLUB':
                return redirect('club_setup')
            elif role == 'SCOUT':
                return redirect('scout_setup')
            elif role == 'MANAGER':
                return redirect('manager_setup')
            elif role == 'FAN':
                return redirect('fan_setup')
    
    return render(request, 'users/select_role.html')


@login_required
def player_setup(request):
    """
    Player profile setup form.
    """
    # Ensure user selected PLAYER role
    if request.user.role != 'PLAYER':
        return redirect('select_role')
    
    # Check if profile already exists
    if hasattr(request.user, 'player_profile'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = PlayerProfileForm()
    
    return render(request, 'users/player_setup.html', {'form': form})


@login_required
def club_setup(request):
    """
    Club profile setup form.
    """
    # Ensure user selected CLUB role
    if request.user.role != 'CLUB':
        return redirect('select_role')
    
    # Check if profile already exists
    if hasattr(request.user, 'club_profile'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClubProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = ClubProfileForm()
    
    return render(request, 'users/club_setup.html', {'form': form})


@login_required
def scout_setup(request):
    """
    Scout profile setup form.
    """
    # Ensure user selected SCOUT role
    if request.user.role != 'SCOUT':
        return redirect('select_role')
    
    # Check if profile already exists
    if hasattr(request.user, 'scout_profile'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ScoutProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = ScoutProfileForm()
    
    return render(request, 'users/scout_setup.html', {'form': form})

@login_required
def manager_setup(request):
    """
    Manager profile setup form.
    """
    # Ensure user selected MANAGER role
    if request.user.role != 'MANAGER':
        return redirect('select_role')
    
    # Check if profile already exists
    if hasattr(request.user, 'manager_profile'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ManagerProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = ManagerProfileForm()
    
    return render(request, 'users/manager_setup.html', {'form': form})
def login_view(request):
    """
    Handles user login.
    Redirects to dashboard (which checks for role) after login.
    """
    from axes.exceptions import AxesBackendRequestParameterRequired
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        try:
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('dashboard')
        except Exception:
            # axes may raise on lockout — form will already contain an error
            pass
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def role_selection_view(request):
    """
    Legacy view - redirects to new select_role view.
    Kept for backwards compatibility.
    """
    return redirect('select_role')

@login_required
def profile_creation_view(request):
    """
    Legacy view - redirects to appropriate setup view based on role.
    Kept for backwards compatibility.
    """
    if not request.user.role:
        return redirect('select_role')
    
    if request.user.role == 'PLAYER':
        return redirect('player_setup')
    elif request.user.role == 'CLUB':
        return redirect('club_setup')
    elif request.user.role == 'SCOUT':
        return redirect('scout_setup')
    else:
        return redirect('dashboard')

@login_required
def dashboard_view(request):
    """
    Main dashboard view.
    Ensures user has selected a role before showing content.
    For players, includes recommended trials based on their profile.
    For managers, includes verification status and career stats.
    """
    if not request.user.role:
        return redirect('select_role')
    
    context = {'user': request.user}
    
    # Add recommendations for players
    if request.user.role == 'PLAYER' and hasattr(request.user, 'player_profile'):
        recommended_trials = get_recommendations(request.user.player_profile)
        context['recommended_trials'] = recommended_trials
    
    # Add manager-specific data
    if request.user.role == 'MANAGER' and hasattr(request.user, 'manager_profile'):
        manager_profile = request.user.manager_profile
        context['manager_profile'] = manager_profile
        # Get pending verification requests
        pending_verifications = manager_profile.verification_requests.filter(status='PENDING').count()
        context['pending_verifications'] = pending_verifications
        # Get all verification requests
        context['verification_requests'] = manager_profile.verification_requests.all()[:5]
        
        # Claim & Verify Feature: Fetch unverified opportunities belonging to this club
        if manager_profile.club_name:
            from .models import Opportunity, ClubProfile
            # Try to find the ClubProfile matching this manager's club name
            club = ClubProfile.objects.filter(club_name__iexact=manager_profile.club_name).first()
            if club:
                unverified_opportunities = Opportunity.objects.filter(
                    club=club, 
                    is_verified=False,
                    is_open=True
                ).order_by('-published_date')
                context['unverified_opportunities'] = unverified_opportunities
    
    return render(request, 'users/dashboard.html', context)

def home_view(request):
    """
    Homepage view displaying latest news and opportunities.
    """
    news_cutoff = timezone.now() - timedelta(days=30)
    
    # Fetch latest 5 news items (last 30 days only)
    latest_news = NewsItem.objects.select_related('club').filter(
        published_date__gte=news_cutoff
    )[:5]
    
    # Fetch latest 5 opportunities (only open ones)
    latest_opportunities = Opportunity.objects.select_related('club').filter(is_open=True)[:5]
    
    context = {
        'latest_news': latest_news,
        'latest_opportunities': latest_opportunities,
    }
    
    return render(request, 'index.html', context)


def feeds_view(request, category=None):
    """
    Unified Feeds page — Shows ALL content from both RSS sources AND registered users.
    
    When no category filter is active ('All Feeds'):
        Shows social posts + all news items combined chronologically.
    When a category filter is active:
        Shows only NewsItems matching that category (no social posts).
    
    Categories: trial, general, transfer, match, recruitment_signal
    """
    from .models import Post
    from itertools import chain
    
    # Recency cutoffs — keep feeds fresh and relevant
    now = timezone.now()
    news_cutoff = now - timedelta(days=30)       # RSS news: last 30 days
    post_cutoff = now - timedelta(days=90)       # Social posts: last 90 days
    
    # Get filter parameters
    post_type_filter = request.GET.get('type', '')
    role_filter = request.GET.get('role', '')
    page_number = request.GET.get('page', 1)
    
    # Fetch all registered club profiles for sidebar
    all_clubs = ClubProfile.objects.all().order_by('league_level', 'club_name')
    
    league_pyramid = {}
    for club in all_clubs:
        level = club.get_league_level_display()
        if level not in league_pyramid:
            league_pyramid[level] = []
        league_pyramid[level].append({
            'name': club.club_name,
            'logo_url': club.logo_url if hasattr(club, 'logo_url') else None,
            'website_url': club.website_url if hasattr(club, 'website_url') else None,
            'type': 'club',
            'is_registered': club.is_registered if hasattr(club, 'is_registered') else True
        })
    
    # Open opportunities sidebar (both RSS and user-posted)
    open_opportunities = Opportunity.objects.filter(
        is_open=True
    ).select_related('source').order_by('-published_date')[:15]
    
    # ── Build the feed based on category ──
    # Exclude Opportunity subclass IDs so we don't double-show them as plain NewsItems
    opportunity_ids = Opportunity.objects.values_list('newsitem_ptr_id', flat=True)
    
    if category:
        # Category-filtered view: show only NewsItems (including Opportunities) for that category
        if category in ('trial', 'recruitment_signal'):
            # For trial/signal tabs, show only OPEN opportunities (hide stale/closed ones)
            feed_items = list(Opportunity.objects.filter(
                category=category,
                is_open=True,
            ).select_related('source').order_by('-published_date'))
        else:
            # For match/transfer/general, show recent news items only (30-day cutoff)
            feed_items = list(NewsItem.objects.filter(
                category=category,
                published_date__gte=news_cutoff,
            ).exclude(
                id__in=opportunity_ids
            ).select_related('source').order_by('-published_date'))
    else:
        # "All Feeds" — combine social posts + all news items, with recency filters
        posts = Post.objects.select_related('user').prefetch_related(
            'likes', 'comments', 'comments__user'
        ).filter(created_at__gte=post_cutoff)
        
        if post_type_filter:
            posts = posts.filter(post_type=post_type_filter)
        if role_filter:
            posts = posts.filter(user__role=role_filter)
        
        # Recent news items only (30-day cutoff), excluding opportunities
        news_items = list(NewsItem.objects.filter(
            published_date__gte=news_cutoff,
        ).exclude(
            id__in=opportunity_ids
        ).select_related('source').order_by('-published_date'))
        
        # Opportunities: only show open ones (regardless of age)
        opportunities = list(Opportunity.objects.filter(
            is_open=True,
        ).select_related('source').order_by('-published_date'))
        
        feed_items = sorted(
            chain(posts, news_items, opportunities),
            key=lambda obj: obj.created_at if hasattr(obj, 'created_at') else obj.published_date,
            reverse=True
        )
    
    # Paginate
    paginator = Paginator(feed_items, 15)
    feed_page = paginator.get_page(page_number)
    
    # Filter choices
    post_types = Post.POST_TYPE_CHOICES
    user_roles = [
        ('PLAYER', 'Players'),
        ('MANAGER', 'Managers'),
        ('CLUB', 'Clubs'),
    ]
    
    total_clubs = ClubProfile.objects.count()
    registered_clubs = ClubProfile.objects.filter(user__isnull=False).count()

    # Category counts for secondary nav — reflect the same recency filters
    category_counts = {
        'trial': Opportunity.objects.filter(category='trial', is_open=True).count(),
        'general': NewsItem.objects.filter(category='general', published_date__gte=news_cutoff).exclude(id__in=opportunity_ids).count(),
        'transfer': NewsItem.objects.filter(category='transfer', published_date__gte=news_cutoff).exclude(id__in=opportunity_ids).count(),
        'match': NewsItem.objects.filter(category='match', published_date__gte=news_cutoff).exclude(id__in=opportunity_ids).count(),
        'recruitment_signal': Opportunity.objects.filter(category='recruitment_signal', is_open=True).count(),
    }
    
    context = {
        'league_pyramid': league_pyramid,
        'feed_items': feed_page,
        'open_opportunities': open_opportunities,
        'total_clubs': total_clubs,
        'registered_clubs': registered_clubs,
        'all_clubs': all_clubs,
        'post_types': post_types,
        'user_roles': user_roles,
        'selected_type': post_type_filter,
        'selected_role': role_filter,
        'current_category': category,
        'category_counts': category_counts,
        'is_feeds_page': True,
    }
    
    return render(request, 'users/feeds_unified.html', context)


def search_clubs(request):
    """
    Search view for Players/Managers to find Clubs.
    Accepts GET parameters: name, level, postcode, league
    """
    import re
    
    # Get search parameters from GET request
    name = request.GET.get('name', '')
    level = request.GET.get('level', '')
    postcode = request.GET.get('postcode', '')
    league = request.GET.get('league', '')
    
    # Start with all club profiles
    clubs = ClubProfile.objects.all()
    
    # Apply filters if provided
    if name:
        # Search by club name (case-insensitive partial match)
        clubs = clubs.filter(club_name__icontains=name.strip())
    
    if level:
        clubs = clubs.filter(league_level=level)
    
    postcode_search_info = ''
    
    if postcode:
        # Smart UK postcode proximity search
        # UK postcodes: outward code = area letters + district number (e.g. "B63", "SW1A")
        # Step 1: Extract area (letters) and outward code (letters + digits before space)
        cleaned = postcode.strip().upper()
        outward_match = re.match(r'^([A-Z]{1,2})(\d{1,2}[A-Z]?)', cleaned)
        
        if outward_match:
            area = outward_match.group(1)          # e.g. "B", "SW"
            outward = outward_match.group(0)       # e.g. "B63", "SW1A"
            
            # Find clubs with exact outward code match first, then same area
            exact_district = clubs.filter(location_postcode__istartswith=outward)
            same_area = clubs.filter(location_postcode__istartswith=area).exclude(
                pk__in=exact_district.values_list('pk', flat=True)
            )
            
            # Combine: exact matches first, then nearby in the same postcode area
            club_list = list(exact_district.order_by('club_name')) + list(same_area.order_by('club_name'))
            
            # Store info for the template
            exact_count = exact_district.count()
            nearby_count = same_area.count()
            if exact_count > 0 and nearby_count > 0:
                postcode_search_info = f'{exact_count} club{"s" if exact_count != 1 else ""} in {outward}, plus {nearby_count} nearby in the {area} postcode area'
            elif exact_count > 0:
                postcode_search_info = f'{exact_count} club{"s" if exact_count != 1 else ""} in {outward}'
            elif nearby_count > 0:
                postcode_search_info = f'No clubs in {outward}, but {nearby_count} found nearby in the {area} postcode area'
            else:
                postcode_search_info = f'No clubs found in the {area} postcode area'
            
            # We'll use the combined list instead of the queryset
            clubs = club_list
        else:
            # Fallback: user entered just letters or partial — match as prefix
            clubs = clubs.filter(location_postcode__istartswith=cleaned)
    
    if league:
        # Search by league name (case-insensitive partial match)
        if isinstance(clubs, list):
            # Already converted to list from postcode search — filter in Python
            league_lower = league.strip().lower()
            clubs = [c for c in clubs if c.league and league_lower in c.league.lower()]
        else:
            clubs = clubs.filter(league__icontains=league.strip())
    
    # Sort by club name (only if still a queryset)
    if not isinstance(clubs, list):
        clubs = clubs.order_by('club_name')
    
    # Get choices for the filter form
    level_choices = ClubProfile.LEAGUE_LEVEL_CHOICES
    
    total_results = len(clubs) if isinstance(clubs, list) else clubs.count()
    
    context = {
        'clubs': clubs,
        'level_choices': level_choices,
        'search_name': name,
        'search_level': level,
        'search_postcode': postcode,
        'search_league': league,
        'total_results': total_results,
        'postcode_search_info': postcode_search_info,
    }
    
    return render(request, 'users/search_clubs.html', context)


def search_players(request):
    """
    Search view for Scouts/Clubs to find Players.
    Accepts GET parameters: position, level, postcode
    Uses Django Q objects to filter PlayerProfile based on inputs.
    """
    # Get search parameters from GET request
    position = request.GET.get('position', '')
    level = request.GET.get('level', '')
    postcode = request.GET.get('postcode', '')
    name = request.GET.get('name', '')
    availability = request.GET.get('availability', '')
    
    # Start with all player profiles that are available
    players = PlayerProfile.objects.select_related('user').filter(
        availability_status__in=['AVAILABLE', 'OPEN', 'TRIALLING']
    )
    
    # Apply filters if provided
    if position:
        players = players.filter(position=position)
    
    if level:
        players = players.filter(playing_level=level)
    
    if postcode:
        # Basic postcode filtering - match players whose postcode starts with the search term
        players = players.filter(location_postcode__istartswith=postcode.strip())
    
    if name:
        # Search by username (case-insensitive partial match)
        players = players.filter(user__username__icontains=name.strip())

    if availability:
        players = players.filter(availability_status=availability)
    
    # Sort by postcode if postcode search is active
    if postcode:
        players = players.order_by('location_postcode')
    else:
        # Default sort by username
        players = players.order_by('user__username')
    
    # Get choices for the filter form
    position_choices = PlayerProfile.POSITION_CHOICES
    level_choices = PlayerProfile.PLAYING_LEVEL_CHOICES
    # Only expose the three statuses that are actually searched — showing
    # CONTRACTED or INJURED in the dropdown would confuse scouts (always 0 results).
    SEARCHABLE_STATUSES = {'AVAILABLE', 'OPEN', 'TRIALLING'}
    availability_choices = [
        c for c in PlayerProfile.AVAILABILITY_CHOICES
        if c[0] in SEARCHABLE_STATUSES
    ]
    
    context = {
        'players': players,
        'position_choices': position_choices,
        'level_choices': level_choices,
        'availability_choices': availability_choices,
        'search_position': position,
        'search_level': level,
        'search_postcode': postcode,
        'search_name': name,
        'search_availability': availability,
        'total_results': players.count(),
    }
    
    return render(request, 'users/search_results.html', context)


@login_required
def edit_profile(request):
    """
    Edit profile view for all user types.
    Routes to appropriate profile edit based on user role.
    """
    if not request.user.role:
        messages.error(request, "Please select a role first.")
        return redirect('select_role')
    
    if request.user.role == 'PLAYER':
        return edit_player_profile(request)
    elif request.user.role == 'CLUB':
        return edit_club_profile(request)
    elif request.user.role == 'SCOUT':
        return edit_scout_profile(request)
    elif request.user.role == 'MANAGER':
        return edit_manager_profile(request)
    else:
        messages.error(request, "Invalid role.")
        return redirect('dashboard')


@login_required
def edit_player_profile(request):
    """
    Edit player profile.
    """
    if request.user.role != 'PLAYER':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    profile = get_object_or_404(PlayerProfile, user=request.user)
    
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = PlayerProfileForm(instance=profile)
    
    return render(request, 'users/player_setup.html', {'form': form, 'edit_mode': True})


@login_required
def edit_club_profile(request):
    """
    Edit club profile.
    """
    if request.user.role != 'CLUB':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    profile = get_object_or_404(ClubProfile, user=request.user)
    
    if request.method == 'POST':
        form = ClubProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = ClubProfileForm(instance=profile)
    
    return render(request, 'users/club_setup.html', {'form': form, 'edit_mode': True})


@login_required
def edit_scout_profile(request):
    """
    Edit scout profile.
    """
    if request.user.role != 'SCOUT':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    profile = get_object_or_404(ScoutProfile, user=request.user)
    
    if request.method == 'POST':
        form = ScoutProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = ScoutProfileForm(instance=profile)
    
    return render(request, 'users/scout_setup.html', {'form': form, 'edit_mode': True})


@login_required
def edit_manager_profile(request):
    """
    Edit manager profile.
    """
    if request.user.role != 'MANAGER':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    profile = get_object_or_404(ManagerProfile, user=request.user)
    
    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = ManagerProfileForm(instance=profile)
    
    return render(request, 'users/manager_setup.html', {'form': form, 'edit_mode': True})


@login_required
def submit_qualification_verification(request):
    """
    Allow managers to submit coaching certificates for Fazz Pitchside verification.
    ALL three pieces of evidence are MANDATORY:
    - Certificate image
    - England Football Learning dashboard screenshot
    - FA FAN Number
    
    A manager cannot submit without providing all three.
    """
    if request.user.role != 'MANAGER':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    if not hasattr(request.user, 'manager_profile'):
        messages.error(request, "Please complete your profile first.")
        return redirect('manager_setup')
    
    manager_profile = request.user.manager_profile
    
    # Get existing verification requests for this manager
    existing_requests = manager_profile.verification_requests.all()
    latest_request = existing_requests.first()  # Most recent (ordered by -submitted_at)
    
    # If they have a pending or approved request, don't allow resubmission
    if latest_request and latest_request.status in ['PENDING', 'APPROVED']:
        if latest_request.status == 'PENDING':
            messages.info(request, "You already have a verification request pending review. Please wait for the admin team to process it.")
        elif latest_request.status == 'APPROVED':
            messages.info(request, "Your qualification has already been verified!")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QualificationVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.manager = manager_profile
            verification.save()
            messages.success(
                request,
                "Your verification request has been submitted successfully! "
                "Our admin team will review your certificate, dashboard screenshot, and FAN number. "
                "This typically takes a few days to a few weeks."
            )
            return redirect('dashboard')
    else:
        form = QualificationVerificationForm()
    
    context = {
        'form': form,
        'existing_requests': existing_requests,
        'latest_request': latest_request,
    }
    
    return render(request, 'users/submit_verification.html', context)


@login_required
def post_opportunity(request):
    """
    Allow clubs to post trial opportunities.
    """
    if request.user.role != 'CLUB':
        messages.error(request, "Only clubs can post opportunities.")
        return redirect('dashboard')
    
    if not hasattr(request.user, 'club_profile'):
        messages.error(request, "Please complete your club profile first.")
        return redirect('club_setup')
    
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.club = request.user.club_profile
            # If no link provided, use a UUID placeholder so the unique constraint
            # is satisfied; we'll update it to the canonical URL after the pk is known.
            if not opportunity.link:
                import uuid as _uuid
                opportunity.link = f'/opportunity/placeholder/{_uuid.uuid4().hex[:16]}/'
            opportunity.save()
            # Replace the placeholder with the canonical URL now that we have a pk
            if '/opportunity/placeholder/' in opportunity.link:
                opportunity.link = f'/opportunity/{opportunity.pk}/'
                opportunity.save()
            # Notify followers that a new trial was posted
            from .models import Follow as FollowModel
            followers = FollowModel.objects.filter(following=request.user).select_related('follower')
            for f in followers:
                create_notification(
                    f.follower,
                    f'{request.user.club_profile.club_name} posted a new trial: {opportunity.title}',
                    'opportunity',
                    f'/opportunity/{opportunity.pk}/'
                )
            messages.success(request, "Trial opportunity posted successfully! It will now appear on the homepage.")
            return redirect('dashboard')
    else:
        form = OpportunityForm()
    
    return render(request, 'users/post_opportunity.html', {'form': form})


def opportunity_detail(request, pk):
    """
    Display full details of a trial opportunity.
    For logged-in players, also:
    - Records a TrialView (behavioral tracking for recommendations)
    - Passes has_applied flag (for Express Interest button state)
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    has_applied = False
    
    # Track view and check application status for logged-in players
    if request.user.is_authenticated and request.user.role == 'PLAYER' and hasattr(request.user, 'player_profile'):
        from .models import TrialView, TrialApplication
        player_profile = request.user.player_profile
        
        # Record or update the view (behavioral tracking)
        trial_view, created = TrialView.objects.get_or_create(
            player=player_profile,
            opportunity=opportunity,
        )
        if not created:
            # Increment view count on repeat visits
            trial_view.view_count += 1
            trial_view.save()
        
        # Check if player has already expressed interest
        has_applied = TrialApplication.objects.filter(
            player=player_profile,
            opportunity=opportunity
        ).exists()
    
    context = {
        'opportunity': opportunity,
        'has_applied': has_applied,
    }
    
    return render(request, 'users/opportunity_detail.html', context)


@login_required
def express_interest(request, pk):
    """
    Allow a player to express interest in a trial opportunity.
    POST-only view. Creates a TrialApplication record.
    
    This data feeds two layers of the recommendation engine:
    - Collaborative filtering: other similar players' interests boost trials
    - Suppression: applied trials are removed from recommendations (-100 score)
    """
    if request.method != 'POST':
        return redirect('opportunity_detail', pk=pk)
    
    if request.user.role != 'PLAYER' or not hasattr(request.user, 'player_profile'):
        messages.error(request, "Only players can express interest in trials.")
        return redirect('opportunity_detail', pk=pk)
    
    from .models import TrialApplication
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Create application (ignore if already exists)
    _, created = TrialApplication.objects.get_or_create(
        player=request.user.player_profile,
        opportunity=opportunity
    )
    
    if created:
        messages.success(request, "Interest registered! The club has been notified.")
    else:
        messages.info(request, "You've already expressed interest in this trial.")
    
    return redirect('opportunity_detail', pk=pk)


@login_required
def withdraw_interest(request, pk):
    """
    Allow a player to withdraw their interest in a trial opportunity.
    POST-only view. Deletes the TrialApplication record.
    """
    if request.method != 'POST':
        return redirect('opportunity_detail', pk=pk)
    
    if request.user.role != 'PLAYER' or not hasattr(request.user, 'player_profile'):
        messages.error(request, "Access denied.")
        return redirect('opportunity_detail', pk=pk)
    
    from .models import TrialApplication
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    TrialApplication.objects.filter(
        player=request.user.player_profile,
        opportunity=opportunity
    ).delete()
    
    messages.success(request, "Interest withdrawn.")
    return redirect('opportunity_detail', pk=pk)

@login_required
def verify_opportunity(request, pk):
    """
    Allow a Club Manager to formally verify an automatically scraped trial.
    This boosts trust and adds a Verified badge to the trial.
    """
    if request.method != 'POST':
        return redirect('opportunity_detail', pk=pk)
        
    if request.user.role != 'MANAGER' or not hasattr(request.user, 'manager_profile'):
        messages.error(request, "Only verified Club Managers can verify trials.")
        return redirect('opportunity_detail', pk=pk)
        
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Security: Manager can only verify trials belonging to their own club
    # ManagerProfile stores club_name as a CharField, so we compare it to the
    # ClubProfile object linked to the opportunity.
    manager_club_name = request.user.manager_profile.club_name
    if not manager_club_name or not opportunity.club or opportunity.club.club_name.lower() != manager_club_name.lower():
        messages.error(request, "You can only verify opportunities belonging to your club.")
        return redirect('opportunity_detail', pk=pk)
        
    opportunity.is_verified = True
    opportunity.verified_by = request.user
    opportunity.save()
    
    messages.success(request, "Trial successfully verified! The Verified badge is now visible to all players.")
    return redirect('opportunity_detail', pk=pk)

def news_detail(request, pk):
    """
    Display full details of a news item or opportunity.
    Unified detail page that keeps users on the platform.
    """
    # Try to get as Opportunity first, then as NewsItem
    try:
        item = Opportunity.objects.get(pk=pk)
        is_opportunity = True
        # Parse target positions into a list
        positions = [pos.strip() for pos in item.target_position.split(',')] if item.target_position else []
    except Opportunity.DoesNotExist:
        item = get_object_or_404(NewsItem, pk=pk)
        is_opportunity = False
        positions = []
    
    context = {
        'item': item,
        'is_opportunity': is_opportunity,
        'positions': positions,
    }
    
    return render(request, 'news_summary.html', context)


def player_profile(request, username):
    """
    Display full player profile with option to message them.
    """
    player_user = get_object_or_404(User, username=username, role='PLAYER')
    player = get_object_or_404(PlayerProfile, user=player_user)
    
    # Position color mapping
    position_colors = {
        'GK': 'bg-yellow-500',  # Yellow for goalkeepers
        'LB': 'bg-blue-500', 'CB': 'bg-blue-600', 'RB': 'bg-blue-500', 'LWB': 'bg-blue-400', 'RWB': 'bg-blue-400',  # Blue shades for defenders
        'CDM': 'bg-green-500', 'CM': 'bg-green-600', 'CAM': 'bg-green-700', 'LM': 'bg-green-500', 'RM': 'bg-green-500',  # Green shades for midfielders
        'LW': 'bg-red-500', 'RW': 'bg-red-500',  # Red for wingers
        'ST': 'bg-purple-600', 'CF': 'bg-purple-700',  # Purple for forwards
    }
    
    context = {
        'player': player,
        'player_user': player_user,
        'position_color': position_colors.get(player.position, 'bg-gray-500'),
        'is_following': False,
        'has_requested': False,
        'on_watchlist': False,
        'on_shortlist': False,
        'follower_count': Follow.objects.filter(following=player_user).count(),
        'following_count': Follow.objects.filter(follower=player_user).count(),
    }
    
    if request.user.is_authenticated and request.user != player_user:
        context['is_following'] = Follow.objects.filter(
            follower=request.user, following=player_user
        ).exists()
        context['has_requested'] = FollowRequest.objects.filter(
            from_user=request.user, to_user=player_user, status='PENDING'
        ).exists()
        if request.user.role == 'SCOUT' and hasattr(request.user, 'scout_profile'):
            context['on_watchlist'] = Watchlist.objects.filter(
                scout=request.user.scout_profile, player=player
            ).exists()
        if request.user.role == 'CLUB' and hasattr(request.user, 'club_profile'):
            context['on_shortlist'] = ClubShortlist.objects.filter(
                club=request.user.club_profile, player=player
            ).exists()
    
    return render(request, 'users/player_profile.html', context)


def community_hub(request):
    """
    Community Hub - Shows RSS AGGREGATED content from external club websites.
    This is for news scraped automatically from ClubSource RSS feeds.
    
    IMPORTANT: Only shows content where source is NOT NULL (RSS feeds),
    NOT user-generated content (which appears in Feeds page).
    
    Includes filtering by league level and pagination.
    """
    from django.core.paginator import Paginator
    
    # Get selected league level filter from query parameter
    selected_level = request.GET.get('level', None)
    page_number = request.GET.get('page', 1)
    
    # Fetch RSS Trials/Opportunities (Only from ClubSource, NOT user posts)
    opportunities = Opportunity.objects.filter(
        source__isnull=False  # Only RSS content
    )
    if selected_level:
        opportunities = opportunities.filter(source__league_level=selected_level)
    opportunities = opportunities.order_by('-published_date')[:10]
    
    # Fetch RSS General News (Only from ClubSource, NOT user posts)
    # Since Opportunity inherits from NewsItem, we need to exclude opportunities from news
    opportunity_ids = Opportunity.objects.values_list('newsitem_ptr_id', flat=True)
    news = NewsItem.objects.filter(
        source__isnull=False  # Only RSS content
    ).exclude(id__in=opportunity_ids)
    if selected_level:
        news = news.filter(source__league_level=selected_level)
    news = news.order_by('-published_date')
    
    # Paginate news (10 items per page)
    paginator = Paginator(news, 10)
    news_page = paginator.get_page(page_number)
    
    # Get league level choices for the filter sidebar
    from .models import ClubSource
    league_levels = ClubSource.LEAGUE_LEVEL_CHOICES
    
    return render(request, 'community_hub.html', {
        'opportunities': opportunities,
        'news': news_page,
        'league_levels': league_levels,
        'selected_level': selected_level,
    })


@login_required
def create_post(request):
    """
    View for creating a new post.
    Available to Players, Managers, and Scouts.
    """
    from .forms import PostForm
    from .models import Post
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('social_feed')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()
    
    return render(request, 'users/create_post.html', {'form': form})


@login_required
def social_feed(request):
    """
    Redirect to unified user feeds.
    This view is kept for backwards compatibility.
    """
    return redirect('feeds')


@login_required
def like_post(request, post_id):
    """
    AJAX view for liking/unliking a post.
    """
    from .models import Post
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            post = Post.objects.get(pk=post_id)
            
            # Toggle like
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
                # Notify post owner
                if post.user != request.user:
                    create_notification(
                        post.user,
                        f'{request.user.username} liked your post.',
                        'like',
                        f'/posts/feed/'
                    )
            
            return JsonResponse({
                'success': True,
                'liked': liked,
                'total_likes': post.total_likes()
            })
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def add_comment(request, post_id):
    """
    AJAX view for adding a comment to a post.
    """
    if request.method == 'POST':
        try:
            post = Post.objects.get(pk=post_id)
            body = request.POST.get('body', '').strip()
            
            if not body:
                return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
            
            if len(body) > 500:
                return JsonResponse({'success': False, 'error': 'Comment must be 500 characters or fewer.'}, status=400)
            
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                body=body
            )
            
            # Notify post owner
            if post.user != request.user:
                create_notification(
                    post.user,
                    f'{request.user.username} commented on your post.',
                    'comment',
                    f'/posts/feed/'
                )
            
            from django.utils.timesince import timesince
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'username': comment.user.username,
                    'body': comment.body,
                    'created_at': timesince(comment.created_at) + ' ago',
                    'can_delete': True,
                },
                'total_comments': post.total_comments()
            })
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_comment(request, comment_id):
    """
    AJAX view for deleting a comment.
    Only the comment author or post owner can delete.
    """
    if request.method == 'POST':
        try:
            comment = Comment.objects.select_related('post').get(pk=comment_id)
            
            if request.user != comment.user and request.user != comment.post.user:
                return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
            
            post = comment.post
            comment.delete()
            
            return JsonResponse({
                'success': True,
                'total_comments': post.total_comments()
            })
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_post(request, post_id):
    """
    View for deleting a post.
    Only the post owner can delete their post.
    """
    from .models import Post
    
    try:
        post = Post.objects.get(pk=post_id)
        
        # Check if user is the post owner
        if post.user != request.user:
            messages.error(request, 'You can only delete your own posts.')
            return redirect('social_feed')
        
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('social_feed')
        
    except Post.DoesNotExist:
        messages.error(request, 'Post not found.')
        return redirect('social_feed')


@login_required
def my_posts(request):
    """
    View for displaying user's own posts.
    """
    from .models import Post
    
    posts = Post.objects.filter(user=request.user).prefetch_related('likes', 'comments', 'comments__user')
    
    # Paginate
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)
    
    context = {
        'posts': posts_page,
        'is_my_posts': True,
    }
    
    return render(request, 'users/my_posts.html', context)


# ---------------------------------------------------------------------------
# Scout Verification Views
# ---------------------------------------------------------------------------

@login_required
def submit_scout_verification(request):
    """
    Allows a scout to submit (or resubmit after rejection) a verification
    application.  Each scout can have at most one ScoutVerification record
    (OneToOneField).  Pending or approved submissions are locked — the scout
    is redirected to the status page instead.
    """
    from django.db import transaction

    if request.user.role != 'SCOUT':
        messages.error(request, 'Only scouts can access this page.')
        return redirect('dashboard')

    if not hasattr(request.user, 'scout_profile'):
        messages.error(request, 'Please complete your scout profile before applying for verification.')
        return redirect('scout_setup')

    scout_profile = request.user.scout_profile

    # Check for an existing verification record
    existing = None
    try:
        existing = ScoutVerification.objects.get(scout=scout_profile)
    except ScoutVerification.DoesNotExist:
        pass

    if existing:
        if existing.status in ('PENDING', 'APPROVED'):
            if existing.status == 'PENDING':
                messages.info(request, 'Your verification application is currently under review. You will be notified of the outcome.')
            else:
                messages.info(request, 'Your scout account is already verified.')
            return redirect('scout_verification_status')
        # REJECTED or FLAGGED — allow the scout to update and resubmit

    if request.method == 'POST':
        form = ScoutVerificationForm(
            request.POST, request.FILES,
            instance=existing if existing else None
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    verification = form.save(commit=False)
                    verification.scout = scout_profile
                    verification.status = 'PENDING'
                    verification.submitted_at = timezone.now()
                    # Clear any previous review data on resubmission
                    verification.reviewed_at = None
                    verification.verified_by = None
                    verification.rejection_reason = ''
                    verification.awarded_tier = ''
                    verification.save()
                messages.success(
                    request,
                    'Your verification has been submitted. '
                    'Review takes a few days to a few weeks. '
                    'You will be notified of the outcome.'
                )
                return redirect('scout_verification_status')
            except Exception as e:
                messages.error(request, f'An error occurred while submitting your application: {e}')
        else:
            messages.error(request, 'Please correct the errors below before submitting.')
    else:
        form = ScoutVerificationForm(instance=existing if existing else None)

    context = {
        'form': form,
        'existing': existing,
        'page_title': 'Scout Verification',
    }
    return render(request, 'users/scout_submit_verification.html', context)


@login_required
def scout_verification_status(request):
    """
    Shows the current status of a scout's verification application.
    """
    if request.user.role != 'SCOUT':
        messages.error(request, 'Only scouts can access this page.')
        return redirect('dashboard')

    if not hasattr(request.user, 'scout_profile'):
        messages.error(request, 'Please complete your scout profile first.')
        return redirect('scout_setup')

    scout_profile = request.user.scout_profile
    verification = None
    try:
        verification = ScoutVerification.objects.get(scout=scout_profile)
    except ScoutVerification.DoesNotExist:
        pass

    # Mark any unread notifications for this user as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    context = {
        'verification': verification,
        'scout_profile': scout_profile,
        'page_title': 'Verification Status',
    }
    return render(request, 'users/scout_verification_status.html', context)


@login_required
def protected_scout_media(request, path):
    """
    Serves scout verification documents only to:
      - The scout who owns the file, or
      - Staff / superusers
    The URL path is relative to MEDIA_ROOT.
    """
    from django.conf import settings

    if not (request.user.is_staff or request.user.is_superuser):
        # Resolve which scout owns the file
        # Build the expected media-relative prefix for this scout
        if not hasattr(request.user, 'scout_profile'):
            raise Http404

        scout_profile = request.user.scout_profile
        try:
            verification = ScoutVerification.objects.get(scout=scout_profile)
        except ScoutVerification.DoesNotExist:
            raise Http404

        # Collect all file fields belonging to this verification
        allowed_paths = set()
        for field_name in (
            'certificate_file', 'dashboard_screenshot',
            'safeguarding_certificate', 'club_affiliation_proof',
            'sample_scout_report',
        ):
            field_file = getattr(verification, field_name)
            if field_file:
                allowed_paths.add(field_file.name)

        if path not in allowed_paths:
            raise Http404

    full_path = os.path.join(settings.MEDIA_ROOT, path)
    # Prevent path traversal
    real_root = os.path.realpath(str(settings.MEDIA_ROOT))
    real_path = os.path.realpath(full_path)
    if not real_path.startswith(real_root):
        raise Http404

    if not os.path.isfile(full_path):
        raise Http404

    return FileResponse(open(full_path, 'rb'))


@login_required
def protected_manager_media(request, path):
    """
    Serves manager verification documents only to:
      - The manager who owns the file, or
      - Staff / superusers
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'manager_profile'):
            raise Http404

        manager_profile = request.user.manager_profile
        verifications = QualificationVerification.objects.filter(manager=manager_profile)
        allowed_paths = set()
        for v in verifications:
            for field_name in ('certificate_image', 'dashboard_screenshot'):
                field_file = getattr(v, field_name)
                if field_file:
                    allowed_paths.add(field_file.name)

        if path not in allowed_paths:
            raise Http404

    full_path = os.path.join(django_settings.MEDIA_ROOT, path)
    # Prevent path traversal
    real_root = os.path.realpath(str(django_settings.MEDIA_ROOT))
    real_path = os.path.realpath(full_path)
    if not real_path.startswith(real_root):
        raise Http404

    if not os.path.isfile(full_path):
        raise Http404

    return FileResponse(open(full_path, 'rb'))


# ===================================================================
# Part 3 – Follow System
# ===================================================================

@login_required
def follow_user(request, user_id):
    """Follow or send a follow request to a user."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    # Already following?
    if Follow.objects.filter(follower=request.user, following=target).exists():
        return JsonResponse({'status': 'already_following'})

    if target.is_private:
        # Create or reuse a pending request
        fr, created = FollowRequest.objects.get_or_create(
            from_user=request.user, to_user=target,
            defaults={'status': 'PENDING'}
        )
        if not created and fr.status == 'REJECTED':
            fr.status = 'PENDING'
            fr.save()
        create_notification(
            target,
            f'{request.user.username} sent you a follow request.',
            'follow_request',
            '/followers/'
        )
        return JsonResponse({'status': 'requested'})
    else:
        Follow.objects.create(follower=request.user, following=target)
        create_notification(
            target,
            f'{request.user.username} started following you.',
            'follow',
            f'/player/{request.user.username}/'
        )
        return JsonResponse({'status': 'following'})


@login_required
def unfollow_user(request, user_id):
    """Unfollow a user."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    target = get_object_or_404(User, pk=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    FollowRequest.objects.filter(from_user=request.user, to_user=target).delete()
    return JsonResponse({'status': 'unfollowed'})


@login_required
def accept_follow_request(request, request_id):
    """Accept a pending follow request."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    fr = get_object_or_404(FollowRequest, pk=request_id, to_user=request.user, status='PENDING')
    fr.status = 'ACCEPTED'
    fr.save()
    Follow.objects.get_or_create(follower=fr.from_user, following=request.user)
    create_notification(
        fr.from_user,
        f'{request.user.username} accepted your follow request.',
        'follow_accepted',
        f'/player/{request.user.username}/'
    )
    return JsonResponse({'status': 'accepted'})


@login_required
def reject_follow_request(request, request_id):
    """Reject a pending follow request."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    fr = get_object_or_404(FollowRequest, pk=request_id, to_user=request.user, status='PENDING')
    fr.status = 'REJECTED'
    fr.save()
    return JsonResponse({'status': 'rejected'})


@login_required
def followers_list(request, user_id):
    """Display a user's followers list."""
    target = get_object_or_404(User, pk=user_id)
    followers = Follow.objects.filter(following=target).select_related('follower')
    pending_requests = []
    if target == request.user:
        pending_requests = FollowRequest.objects.filter(to_user=request.user, status='PENDING').select_related('from_user')
    return render(request, 'users/followers_list.html', {
        'profile_user': target,
        'followers': followers,
        'pending_requests': pending_requests,
    })


@login_required
def following_list(request, user_id):
    """Display users that a user is following."""
    target = get_object_or_404(User, pk=user_id)
    following = Follow.objects.filter(follower=target).select_related('following')
    return render(request, 'users/following_list.html', {
        'profile_user': target,
        'following': following,
    })


# ===================================================================
# Part 4 – Private Messaging / DMs
# ===================================================================

@login_required
def inbox_view(request):
    """Display user's conversation inbox."""
    conversations = request.user.conversations.all().order_by('-updated_at')
    conv_data = []
    for conv in conversations:
        other = conv.get_other_participant(request.user)
        last_msg = conv.get_last_message()
        unread = conv.unread_count(request.user)
        conv_data.append({
            'conversation': conv,
            'other_user': other,
            'last_message': last_msg,
            'unread': unread,
        })
    return render(request, 'users/inbox.html', {'conversations': conv_data})


@login_required
def conversation_view(request, conversation_id):
    """View and send messages in a conversation."""
    conv = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in conv.participants.all():
        raise Http404

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            msg = Message.objects.create(conversation=conv, sender=request.user, body=body)
            conv.save()  # bump updated_at
            other = conv.get_other_participant(request.user)
            if other:
                create_notification(
                    other,
                    f'New message from {request.user.username}',
                    'message',
                    f'/messages/{conv.id}/'
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'sent',
                    'message': {
                        'id': msg.id,
                        'body': msg.body,
                        'sender': msg.sender.username,
                        'sent_at': msg.sent_at.strftime('%H:%M'),
                    }
                })
            return redirect('conversation', conversation_id=conv.id)

    # Mark messages from other user as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    all_messages = conv.messages.all()
    other_user = conv.get_other_participant(request.user)
    return render(request, 'users/conversation.html', {
        'conversation': conv,
        'messages': all_messages,
        'other_user': other_user,
    })


@login_required
def start_conversation(request, user_id):
    """Start a new conversation or redirect to existing one."""
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('inbox')

    # Privacy check – must follow private users
    if other.is_private:
        is_follower = Follow.objects.filter(follower=request.user, following=other).exists()
        if not is_follower:
            messages.error(request, "You must follow this user to send a message.")
            return redirect('inbox')

    # Check for existing conversation between these two
    existing = Conversation.objects.filter(participants=request.user).filter(participants=other)
    for conv in existing:
        if conv.participants.count() == 2:
            return redirect('conversation', conversation_id=conv.id)

    # Create new conversation
    conv = Conversation.objects.create()
    conv.participants.add(request.user, other)
    return redirect('conversation', conversation_id=conv.id)


@login_required
def get_new_messages(request, conversation_id):
    """AJAX endpoint – poll for new messages after a given ID."""
    conv = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in conv.participants.all():
        return JsonResponse({'error': 'forbidden'}, status=403)

    after_id = int(request.GET.get('after', 0))
    new_msgs = conv.messages.filter(id__gt=after_id).order_by('sent_at')
    # Mark them read
    new_msgs.exclude(sender=request.user).update(is_read=True)
    data = [{
        'id': m.id,
        'body': m.body,
        'sender': m.sender.username,
        'is_mine': m.sender == request.user,
        'sent_at': m.sent_at.strftime('%H:%M'),
    } for m in new_msgs]
    return JsonResponse({'messages': data})


@login_required
def get_unread_count(request):
    """Return total unread message count for the current user (JSON)."""
    total = 0
    for conv in request.user.conversations.all():
        total += conv.unread_count(request.user)
    return JsonResponse({'unread': total})


# ===================================================================
# Part 5 – Notifications
# ===================================================================

@login_required
def notifications_view(request):
    """Full notifications page."""
    notifs = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifs, 30)
    page = paginator.get_page(request.GET.get('page'))
    # Mark them as read
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'users/notifications.html', {'page_obj': page})


@login_required
def get_notification_count(request):
    """AJAX endpoint – unread notification count."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_notifications_dropdown(request):
    """Return recent notifications as JSON for the dropdown."""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [{
        'id': n.id,
        'message': n.message,
        'type': n.notification_type,
        'action_url': n.action_url,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%d %b %H:%M'),
    } for n in notifs]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread})


# ===================================================================
# Part 7 – Watchlist / Shortlist
# ===================================================================

@login_required
def add_to_watchlist(request, player_id):
    """Scout adds a player to their watchlist."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if request.user.role != 'SCOUT' or not hasattr(request.user, 'scout_profile'):
        return JsonResponse({'error': 'Scout access only'}, status=403)

    player = get_object_or_404(PlayerProfile, pk=player_id)
    obj, created = Watchlist.objects.get_or_create(
        scout=request.user.scout_profile, player=player
    )
    return JsonResponse({'status': 'added' if created else 'already_exists', 'id': obj.id})


@login_required
def remove_from_watchlist(request, player_id):
    """Scout removes a player from their watchlist."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if request.user.role != 'SCOUT' or not hasattr(request.user, 'scout_profile'):
        return JsonResponse({'error': 'Scout access only'}, status=403)

    player = get_object_or_404(PlayerProfile, pk=player_id)
    Watchlist.objects.filter(scout=request.user.scout_profile, player=player).delete()
    return JsonResponse({'status': 'removed'})


@login_required
def scout_watchlist_view(request):
    """Display scout's watchlist."""
    if request.user.role != 'SCOUT' or not hasattr(request.user, 'scout_profile'):
        messages.error(request, 'Scout access only.')
        return redirect('dashboard')

    watchlist = Watchlist.objects.filter(scout=request.user.scout_profile).select_related('player__user')
    return render(request, 'users/scout_watchlist.html', {'watchlist': watchlist})


@login_required
def update_watchlist_notes(request, watchlist_id):
    """Update private notes on a watchlist entry (AJAX)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    entry = get_object_or_404(Watchlist, pk=watchlist_id, scout=request.user.scout_profile)
    notes = request.POST.get('notes', '')
    entry.private_notes = notes
    entry.save()
    return JsonResponse({'status': 'updated'})


@login_required
def add_to_shortlist(request, player_id):
    """Club adds a player to their shortlist."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if request.user.role != 'CLUB' or not hasattr(request.user, 'club_profile'):
        return JsonResponse({'error': 'Club access only'}, status=403)

    player = get_object_or_404(PlayerProfile, pk=player_id)
    opportunity_id = request.POST.get('opportunity_id')
    opp = None
    if opportunity_id:
        opp = Opportunity.objects.filter(pk=opportunity_id).first()

    obj, created = ClubShortlist.objects.get_or_create(
        club=request.user.club_profile, player=player,
        defaults={'opportunity': opp}
    )
    return JsonResponse({'status': 'added' if created else 'already_exists', 'id': obj.id})


@login_required
def remove_from_shortlist(request, player_id):
    """Club removes a player from their shortlist."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if request.user.role != 'CLUB' or not hasattr(request.user, 'club_profile'):
        return JsonResponse({'error': 'Club access only'}, status=403)

    player = get_object_or_404(PlayerProfile, pk=player_id)
    ClubShortlist.objects.filter(club=request.user.club_profile, player=player).delete()
    return JsonResponse({'status': 'removed'})


@login_required
def club_shortlist_view(request):
    """Display club's shortlisted players."""
    if request.user.role != 'CLUB' or not hasattr(request.user, 'club_profile'):
        messages.error(request, 'Club access only.')
        return redirect('dashboard')

    shortlist = ClubShortlist.objects.filter(club=request.user.club_profile).select_related('player__user', 'opportunity')
    return render(request, 'users/club_shortlist.html', {'shortlist': shortlist})


# ===================================================================
# Part 9 – AI Bio Generator
# ===================================================================

@login_required
def generate_bio_view(request):
    """AJAX endpoint – generate a player bio via Gemini AI."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if request.user.role != 'PLAYER' or not hasattr(request.user, 'player_profile'):
        return JsonResponse({'error': 'Player access only'}, status=403)

    try:
        from .utils_ai import generate_player_bio
        bio = generate_player_bio(request.user.player_profile)
        return JsonResponse({'status': 'ok', 'bio': bio})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ===================================================================
# Part 10 – Fan Profile Setup
# ===================================================================

@login_required
def fan_setup(request):
    """Fan profile setup form."""
    if request.user.role != 'FAN':
        return redirect('select_role')

    if hasattr(request.user, 'fan_profile'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = FanProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Welcome to Fazz Pitchside Hub!')
            return redirect('dashboard')
    else:
        form = FanProfileForm()

    return render(request, 'users/fan_setup.html', {'form': form})


# ===================================================================
# Part 12 – Security / GDPR
# ===================================================================

@login_required
def delete_account_view(request):
    """Allow a user to delete their own account."""
    if request.method == 'POST':
        confirm = request.POST.get('confirm_delete')
        if confirm == 'DELETE':
            user = request.user
            from django.contrib.auth import logout
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Please type DELETE to confirm account removal.')

    return render(request, 'users/delete_account.html')


def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'users/privacy_policy.html')


@login_required
def export_data_view(request):
    """GDPR data export — download all personal data as JSON."""
    user = request.user
    data = {
        'account': {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_private': user.is_private,
            'is_email_verified': user.is_email_verified,
            'privacy_consent': user.privacy_consent,
            'privacy_consent_date': user.privacy_consent_date.isoformat() if user.privacy_consent_date else None,
        },
    }

    # Role-specific profile
    profile_map = {
        'PLAYER': ('player_profile', [
            'position', 'location_postcode', 'playing_level', 'height', 'weight',
            'preferred_foot', 'bio', 'availability', 'available_for_club',
            'date_of_birth',
        ]),
        'CLUB': ('club_profile', [
            'club_name', 'location', 'location_postcode', 'league_level',
            'bio', 'website_url', 'founded_year', 'contact_email',
        ]),
        'SCOUT': ('scout_profile', [
            'location', 'bio', 'scouting_level', 'affiliated_club',
            'years_experience',
        ]),
        'MANAGER': ('manager_profile', [
            'location', 'bio', 'current_club', 'coaching_level',
            'years_experience',
        ]),
        'FAN': ('fan_profile', [
            'bio', 'favourite_club',
        ]),
    }

    if user.role and user.role in profile_map:
        attr, fields = profile_map[user.role]
        if hasattr(user, attr):
            profile = getattr(user, attr)
            profile_data = {}
            for f in fields:
                val = getattr(profile, f, None)
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                elif val is not None:
                    val = str(val)
                profile_data[f] = val
            data['profile'] = profile_data

    # Posts
    data['posts'] = list(
        Post.objects.filter(author=user).values('id', 'content', 'created_at')
    )
    # Comments
    data['comments'] = list(
        Comment.objects.filter(author=user).values('id', 'content', 'created_at', 'post_id')
    )
    # Follows
    data['following'] = list(
        Follow.objects.filter(follower=user).values_list('following__username', flat=True)
    )
    data['followers'] = list(
        Follow.objects.filter(following=user).values_list('follower__username', flat=True)
    )
    # Messages
    conversations = Conversation.objects.filter(participants=user)
    msgs = Message.objects.filter(conversation__in=conversations, sender=user)
    data['messages_sent'] = list(
        msgs.values('id', 'content', 'created_at', 'conversation_id')
    )
    # Watchlist / Shortlist
    data['watchlist'] = list(
        Watchlist.objects.filter(scout__user=user).values('player__user__username', 'notes', 'added_at')
    ) if user.role == 'SCOUT' else []
    data['shortlist'] = list(
        ClubShortlist.objects.filter(club__user=user).values('player__user__username', 'notes', 'added_at')
    ) if user.role == 'CLUB' else []

    # Serialise with date support
    response = JsonResponse(data, json_dumps_params={'indent': 2, 'default': str})
    response['Content-Disposition'] = f'attachment; filename="fazz_data_export_{user.username}.json"'
    return response


def about_page(request):
    """About page."""
    return render(request, 'users/about.html')


def contact_page(request):
    """Contact page."""
    return render(request, 'users/contact.html')


# =========================================================================
# Football Pathways — Educational Hub
# =========================================================================

def pathways_home(request):
    """Football Pathways landing page — choose your journey."""
    return render(request, 'pathways/home.html')


def pathways_player(request):
    """Become a Player — pathway, trials, development."""
    return render(request, 'pathways/player.html')


def pathways_manager(request):
    """Become a Manager — qualifications, career path."""
    return render(request, 'pathways/manager.html')


def pathways_scout(request):
    """Become a Scout — what scouts do, qualifications, reports."""
    return render(request, 'pathways/scout.html')


def pathways_non_league(request):
    """Understanding Non-League Football — the pyramid explained."""
    return render(request, 'pathways/non_league.html')


def pathways_qualifications(request):
    """Football Qualifications — coaching, talent ID, safeguarding."""
    return render(request, 'pathways/qualifications.html')


@login_required
def security_settings(request):
    """User security settings page: toggle privacy, change password link."""
    if request.method == 'POST':
        is_private = request.POST.get('is_private') == 'on'
        request.user.is_private = is_private
        request.user.save(update_fields=['is_private'])

        # Scout stealth toggle
        if request.user.role == 'SCOUT' and hasattr(request.user, 'scout_profile'):
            is_scout_public = request.POST.get('is_scout_public') == 'on'
            request.user.scout_profile.is_scout_public = is_scout_public
            request.user.scout_profile.save(update_fields=['is_scout_public'])

        messages.success(request, 'Privacy settings updated.')
        return redirect('security_settings')

    return render(request, 'users/security_settings.html')
