from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .forms import (
    CustomUserCreationForm, PlayerProfileForm, ClubProfileForm, 
    ScoutProfileForm, ManagerProfileForm, QualificationVerificationForm,
    OpportunityForm
)
from .models import (
    User, NewsItem, Opportunity, PlayerProfile, ClubProfile, ClubSource,
    ScoutProfile, ManagerProfile, QualificationVerification
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
    Feeds page - Shows all clubs organized by league level,
    with their latest news and opportunities from RSS feeds and user posts.
    Displays both ClubSource (RSS aggregation) and ClubProfile (registered users) content.
    """
    # Fetch all club sources (RSS aggregation)
    all_sources = ClubSource.objects.all().order_by('league_level', 'name')
    
    # Fetch all registered club profiles
    all_clubs = ClubProfile.objects.all().order_by('league_level', 'club_name')
    
    # Organize club sources by league level for pyramid display
    league_pyramid = {}
    for source in all_sources:
        level = source.get_league_level_display()
        if level not in league_pyramid:
            league_pyramid[level] = []
        league_pyramid[level].append({
            'name': source.name,
            'logo_url': source.logo_url,
            'website_url': source.website_url,
            'type': 'source'
        })
    
    # Add registered clubs to the league pyramid
    for club in all_clubs:
        level = club.get_league_level_display()
        if level not in league_pyramid:
            league_pyramid[level] = []
        league_pyramid[level].append({
            'name': club.club_name,
            'logo_url': club.logo_url,
            'website_url': club.website_url,
            'type': 'club'
        })
    
    # Fetch latest news from all sources (both RSS and user posts)
    latest_news = NewsItem.objects.select_related('source', 'club').all().order_by('-published_date')[:20]
    
    # Fetch open opportunities
    open_opportunities = Opportunity.objects.select_related('source', 'club').filter(is_open=True).order_by('-published_date')[:15]
    
    # Get sources with RSS feeds configured
    sources_with_rss = ClubSource.objects.exclude(rss_url='').count()
    total_sources = ClubSource.objects.count()
    
    # Get clubs with RSS feeds configured
    clubs_with_rss = ClubProfile.objects.exclude(rss_feed_url='').count()
    total_clubs = ClubProfile.objects.count()
    
    context = {
        'league_pyramid': league_pyramid,
        'latest_news': latest_news,
        'open_opportunities': open_opportunities,
        'sources_with_rss': sources_with_rss,
        'total_sources': total_sources,
        'clubs_with_rss': clubs_with_rss,
        'total_clubs': total_clubs,
        'all_sources': all_sources,
        'all_clubs': all_clubs,
    }
    
    return render(request, 'users/feeds.html', context)


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
    Display full details of a news item.
    """
    news = get_object_or_404(NewsItem, pk=pk)
    
    context = {
        'news': news,
    }
    
    return render(request, 'users/news_detail.html', context)


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
