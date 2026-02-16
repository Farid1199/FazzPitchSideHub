from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from itertools import chain
from .forms import (
    CustomUserCreationForm, PlayerProfileForm, ClubProfileForm, 
    ScoutProfileForm, ManagerProfileForm, QualificationVerificationForm,
    OpportunityForm, PostForm
)
from .models import (
    User, NewsItem, Opportunity, PlayerProfile, ClubProfile, ClubSource,
    ScoutProfile, ManagerProfile, QualificationVerification, Post
)
from .utils import get_recommendations

def signup_view(request):
    """
    Handles user registration.
    Redirects to role selection after successful signup.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('select_role')  # Redirect to role selection
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
    
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['PLAYER', 'CLUB', 'SCOUT', 'MANAGER']:
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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
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
    
    return render(request, 'users/dashboard.html', context)

def home_view(request):
    """
    Homepage view displaying latest news and opportunities.
    """
    # Fetch latest 5 news items
    latest_news = NewsItem.objects.select_related('club').all()[:5]
    
    # Fetch latest 5 opportunities (only open ones)
    latest_opportunities = Opportunity.objects.select_related('club').filter(is_open=True)[:5]
    
    context = {
        'latest_news': latest_news,
        'latest_opportunities': latest_opportunities,
    }
    
    return render(request, 'index.html', context)


def feeds_view(request):
    """
    User Feeds page - Shows ALL content posted BY REGISTERED USERS on the platform.
    This includes:
    - Club news and opportunities (NewsItems/Opportunities)
    - Player/Manager/Scout posts (Posts with achievements, highlights, etc.)
    
    IMPORTANT: Only shows user-generated content, NOT RSS aggregated content.
    """
    from .models import Post
    from itertools import chain
    from operator import attrgetter
    
    # Get filter parameters
    post_type_filter = request.GET.get('type', '')
    role_filter = request.GET.get('role', '')
    page_number = request.GET.get('page', 1)
    
    # Fetch all registered club profiles
    all_clubs = ClubProfile.objects.all().order_by('league_level', 'club_name')
    
    # Organize registered clubs by league level for pyramid display
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
    
    # Fetch USER-GENERATED opportunities (only from registered clubs, NOT RSS)
    open_opportunities = Opportunity.objects.filter(
        club__isnull=False,  # Only user posts
        is_open=True
    ).select_related('club').order_by('-published_date')[:15]
    
    # Fetch social posts from players/managers/scouts
    posts = Post.objects.select_related('user').prefetch_related('likes').all()
    
    # Apply filters to posts
    if post_type_filter:
        posts = posts.filter(post_type=post_type_filter)
    if role_filter:
        posts = posts.filter(user__role=role_filter)
    
    # Fetch club news items
    club_news = NewsItem.objects.filter(
        club__isnull=False  # Only user posts
    ).select_related('club')
    
    # Combine and sort all content by date (most recent first)
    # We'll paginate the combined feed
    combined_feed = sorted(
        chain(posts, club_news),
        key=lambda obj: obj.created_at if hasattr(obj, 'created_at') else obj.published_date,
        reverse=True
    )
    
    # Paginate combined feed (15 items per page)
    paginator = Paginator(combined_feed, 15)
    feed_page = paginator.get_page(page_number)
    
    # Get filter choices
    post_types = Post.POST_TYPE_CHOICES
    user_roles = [
        ('PLAYER', 'Players'),
        ('MANAGER', 'Managers'),
        ('SCOUT', 'Scouts'),
        ('CLUB', 'Clubs'),
    ]
    
    # Get registered clubs count
    total_clubs = ClubProfile.objects.count()
    registered_clubs = ClubProfile.objects.filter(user__isnull=False).count()
    
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
    }
    
    return render(request, 'users/feeds_unified.html', context)


def search_clubs(request):
    """
    Search view for Players/Managers to find Clubs.
    Accepts GET parameters: name, level, postcode, league
    """
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
    
    if postcode:
        # Basic postcode filtering - match clubs whose postcode starts with the search term
        clubs = clubs.filter(location_postcode__istartswith=postcode.strip())
    
    if league:
        # Search by league name (case-insensitive partial match)
        clubs = clubs.filter(league__icontains=league.strip())
    
    # Sort by club name
    clubs = clubs.order_by('club_name')
    
    # Get choices for the filter form
    level_choices = ClubProfile.LEAGUE_LEVEL_CHOICES
    
    context = {
        'clubs': clubs,
        'level_choices': level_choices,
        'search_name': name,
        'search_level': level,
        'search_postcode': postcode,
        'search_league': league,
        'total_results': clubs.count(),
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
    
    # Start with all player profiles that are available
    players = PlayerProfile.objects.select_related('user').filter(available_for_club=True)
    
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
    
    # Sort by postcode if postcode search is active
    if postcode:
        players = players.order_by('location_postcode')
    else:
        # Default sort by username
        players = players.order_by('user__username')
    
    # Get choices for the filter form
    position_choices = PlayerProfile.POSITION_CHOICES
    level_choices = PlayerProfile.PLAYING_LEVEL_CHOICES
    
    context = {
        'players': players,
        'position_choices': position_choices,
        'level_choices': level_choices,
        'search_position': position,
        'search_level': level,
        'search_postcode': postcode,
        'search_name': name,
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
    Allow managers to submit coaching certificates for verification.
    """
    if request.user.role != 'MANAGER':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    if not hasattr(request.user, 'manager_profile'):
        messages.error(request, "Please complete your profile first.")
        return redirect('manager_setup')
    
    if request.method == 'POST':
        form = QualificationVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.manager = request.user.manager_profile
            verification.save()
            messages.success(request, "Certificate submitted successfully! It will be reviewed by our admin team.")
            return redirect('dashboard')
    else:
        form = QualificationVerificationForm()
    
    return render(request, 'users/submit_verification.html', {'form': form})


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
            # If no link provided, use a placeholder
            if not opportunity.link:
                opportunity.link = '#'
            opportunity.save()
            messages.success(request, "Trial opportunity posted successfully! It will now appear on the homepage.")
            return redirect('dashboard')
    else:
        form = OpportunityForm()
    
    return render(request, 'users/post_opportunity.html', {'form': form})


def opportunity_detail(request, pk):
    """
    Display full details of a trial opportunity.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    context = {
        'opportunity': opportunity,
    }
    
    return render(request, 'users/opportunity_detail.html', context)


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
    }
    
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
            
            return JsonResponse({
                'success': True,
                'liked': liked,
                'total_likes': post.total_likes()
            })
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)
    
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
    
    posts = Post.objects.filter(user=request.user).prefetch_related('likes')
    
    # Paginate
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)
    
    context = {
        'posts': posts_page,
        'is_my_posts': True,
    }
    
    return render(request, 'users/my_posts.html', context)
