"""
Script to create test player profiles for search functionality demonstration.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, PlayerProfile

# Test data for players
test_players = [
    {
        'username': 'john_striker',
        'email': 'john@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'ST',
            'location_postcode': 'SW1A 1AA',
            'playing_level': 'STEP_5',
            'height': 1.82,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Local FC, Community United',
        }
    },
    {
        'username': 'sarah_midfielder',
        'email': 'sarah@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'CM',
            'location_postcode': 'SW1A 2AB',
            'playing_level': 'STEP_6',
            'height': 1.68,
            'preferred_foot': 'BOTH',
            'previous_clubs': 'City Youth, Regional FC',
        }
    },
    {
        'username': 'mike_keeper',
        'email': 'mike@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'GK',
            'location_postcode': 'M1 1AA',
            'playing_level': 'STEP_4',
            'height': 1.91,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Manchester Academy, Local Rangers',
        }
    },
    {
        'username': 'emma_winger',
        'email': 'emma@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'LW',
            'location_postcode': 'M1 2BB',
            'playing_level': 'STEP_5',
            'height': 1.65,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Youth Stars, Athletic Club',
            'youtube_highlight_url': 'https://youtube.com/watch?v=example',
        }
    },
    {
        'username': 'james_defender',
        'email': 'james@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'CB',
            'location_postcode': 'B1 1AA',
            'playing_level': 'STEP_3',
            'height': 1.88,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Birmingham Youth, County FC',
        }
    },
    {
        'username': 'lisa_forward',
        'email': 'lisa@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'CF',
            'location_postcode': 'B1 2CC',
            'playing_level': 'STEP_6',
            'height': 1.70,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Local Warriors',
        }
    },
    {
        'username': 'tom_wingback',
        'email': 'tom@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'RWB',
            'location_postcode': 'L1 1AA',
            'playing_level': 'SUNDAY',
            'height': 1.75,
            'preferred_foot': 'BOTH',
            'previous_clubs': 'Sunday League FC, Park Rangers',
        }
    },
    {
        'username': 'amy_midfielder',
        'email': 'amy@example.com',
        'password': 'testpass123',
        'role': 'PLAYER',
        'profile': {
            'position': 'CAM',
            'location_postcode': 'L1 2DD',
            'playing_level': 'STEP_7',
            'height': 1.63,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Youth Academy',
        }
    },
]

def create_test_players():
    """Create test player accounts and profiles."""
    print("Creating test player profiles...")
    
    for player_data in test_players:
        # Check if user already exists
        if User.objects.filter(username=player_data['username']).exists():
            print(f"  ⚠ User '{player_data['username']}' already exists, skipping...")
            continue
        
        # Create user
        user = User.objects.create_user(
            username=player_data['username'],
            email=player_data['email'],
            password=player_data['password'],
            role=player_data['role']
        )
        
        # Update the auto-created profile with test data
        profile = user.player_profile
        for key, value in player_data['profile'].items():
            setattr(profile, key, value)
        profile.save()
        
        print(f"  ✓ Created player: {player_data['username']} ({player_data['profile']['position']}) - {player_data['profile']['location_postcode']}")
    
    print(f"\n✅ Test data creation complete!")
    print(f"Total players in database: {PlayerProfile.objects.count()}")

if __name__ == '__main__':
    create_test_players()
