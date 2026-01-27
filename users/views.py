from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .forms import CustomUserCreationForm, PlayerProfileForm, ClubProfileForm, ScoutProfileForm, ManagerProfileForm
from .models import User, NewsItem, Opportunity, PlayerProfile
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
        form = PlayerProfileForm(request.POST)
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
    """
    if not request.user.role:
        return redirect('select_role')
    
    context = {'user': request.user}
    
    # Add recommendations for players
    if request.user.role == 'PLAYER' and hasattr(request.user, 'player_profile'):
        recommended_trials = get_recommendations(request.user.player_profile)
        context['recommended_trials'] = recommended_trials
    
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
    
    # Start with all player profiles
    players = PlayerProfile.objects.select_related('user').all()
    
    # Build query using Q objects for filtering
    query = Q()
    
    if position:
        query &= Q(position=position)
    
    if level:
        query &= Q(playing_level=level)
    
    if postcode:
        # Basic postcode filtering - sort by similarity
        # For now, we'll filter players whose postcode starts with the search term
        query &= Q(location_postcode__istartswith=postcode.strip())
    
    # Apply filters
    if query:
        players = players.filter(query)
    
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
        'total_results': players.count(),
    }
    
    return render(request, 'users/search_results.html', context)

