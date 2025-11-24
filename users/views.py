from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, PlayerProfileForm, ClubProfileForm, ScoutProfileForm
from .models import CustomUser

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
            return redirect('role_selection')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

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
    Allows the user to select their role (Player, Club, Scout).
    If role is already selected, redirects to dashboard.
    """
    if request.user.is_role_selected:
        return redirect('dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['PLAYER', 'CLUB', 'SCOUT']:
            request.user.user_type = role
            request.user.save()
            return redirect('profile_creation')
    
    return render(request, 'users/role_selection.html')

@login_required
def profile_creation_view(request):
    """
    Displays the specific profile form based on the user's selected role.
    """
    user = request.user
    if user.is_role_selected:
        return redirect('dashboard')
    
    # Determine which form to use based on user_type
    if user.user_type == 'PLAYER':
        form_class = PlayerProfileForm
    elif user.user_type == 'CLUB':
        form_class = ClubProfileForm
    elif user.user_type == 'SCOUT':
        form_class = ScoutProfileForm
    else:
        return redirect('role_selection')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Mark role as selected and profile complete
            user.is_role_selected = True
            user.save()
            return redirect('dashboard')
    else:
        form = form_class()

    return render(request, 'users/profile_creation.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Main dashboard view.
    Ensures user has selected a role before showing content.
    """
    if not request.user.is_role_selected:
        return redirect('role_selection')
    
    return render(request, 'users/dashboard.html', {'user': request.user})

def home_view(request):
    return render(request, 'users/home.html')
