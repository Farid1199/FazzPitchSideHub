"""
Display all test user login credentials
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import PlayerProfile, ManagerProfile

User = get_user_model()

def display_credentials():
    print()
    print("=" * 80)
    print("🔑 TEST USER LOGIN CREDENTIALS - FAZZPITCHSIDEHUB")
    print("=" * 80)
    print()
    print("⚠️  ALL PASSWORDS ARE: TestPass123!")
    print()
    
    # Get all players
    players = User.objects.filter(role='PLAYER').select_related('player_profile').order_by('player_profile__position', 'username')
    
    # Group by position
    players_by_position = {}
    for player in players:
        if hasattr(player, 'player_profile'):
            position = player.player_profile.position
            if position not in players_by_position:
                players_by_position[position] = []
            players_by_position[position].append(player)
    
    position_names = {
        'GK': 'Goalkeepers',
        'LB': 'Left Backs',
        'CB': 'Centre Backs',
        'RB': 'Right Backs',
        'CDM': 'Defensive Midfielders',
        'CM': 'Central Midfielders',
        'CAM': 'Attacking Midfielders',
        'LW': 'Left Wingers',
        'RW': 'Right Wingers',
        'ST': 'Strikers',
        'CF': 'Centre Forwards',
    }
    
    print("👥 PLAYERS BY POSITION")
    print("-" * 80)
    
    for position in ['GK', 'LB', 'CB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST', 'CF']:
        if position in players_by_position:
            print(f"\n{position_names.get(position, position)}:")
            for player in players_by_position[position]:
                profile = player.player_profile
                print(f"  • Username: {player.username}")
                print(f"    Email: {player.email}")
                print(f"    Password: TestPass123!")
                print(f"    Level: {profile.get_playing_level_display()}")
                print(f"    Location: {profile.location_postcode}")
                print(f"    Available: {'Yes' if profile.available_for_club else 'No'}")
                print()
    
    # Get all managers
    managers = User.objects.filter(role='MANAGER').select_related('manager_profile').order_by('username')
    
    print("=" * 80)
    print("👔 MANAGERS")
    print("-" * 80)
    
    for manager in managers:
        if hasattr(manager, 'manager_profile'):
            profile = manager.manager_profile
            print(f"\n• Username: {manager.username}")
            print(f"  Email: {manager.email}")
            print(f"  Password: TestPass123!")
            print(f"  Qualification: {profile.get_highest_qualification_display()}")
            print(f"  Experience: {profile.years_of_experience} years")
            print(f"  Availability: {profile.get_availability_display()}")
            if profile.club_name:
                print(f"  Current Club: {profile.club_name}")
            print()
    
    print("=" * 80)
    print()
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Players: {players.count()}")
    print(f"Total Managers: {managers.count()}")
    print()
    print("=" * 80)
    print()
    print("💡 QUICK TIPS:")
    print("  • All passwords are: TestPass123!")
    print("  • Player usernames: <position>_<name> (e.g., st_harry, gk_james)")
    print("  • Manager usernames: manager_<name> (e.g., manager_pep)")
    print("  • Login at: http://localhost:8000/login/")
    print()
    print("=" * 80)

if __name__ == '__main__':
    display_credentials()
