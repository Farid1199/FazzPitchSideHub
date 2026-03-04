"""
Script to create test manager profiles for verification system demonstration.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, ManagerProfile

# Test data for managers
# No qualifications added; only basic profile info

test_managers = [
    {
        'username': 'alex_coach',
        'email': 'alex.coach@example.com',
        'password': 'testpass123',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'Alexandra FC',
            'location_postcode': 'SW1A 3AA',
        }
    },
    {
        'username': 'nina_manager',
        'email': 'nina.manager@example.com',
        'password': 'testpass123',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'Nina United',
            'location_postcode': 'M1 3BB',
        }
    },
    {
        'username': 'david_boss',
        'email': 'david.boss@example.com',
        'password': 'testpass123',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'David City',
            'location_postcode': 'B1 3CC',
        }
    },
    {
        'username': 'sophie_gaffer',
        'email': 'sophie.gaffer@example.com',
        'password': 'testpass123',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'Sophie Athletic',
            'location_postcode': 'L1 3DD',
        }
    },
    {
        'username': 'liam_headcoach',
        'email': 'liam.headcoach@example.com',
        'password': 'testpass123',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'Liam Rovers',
            'location_postcode': 'E1 3EE',
        }
    },
]

def create_test_managers():
    """Create test manager accounts and profiles."""
    print("Creating test manager profiles...")
    for manager_data in test_managers:
        # Check if user already exists
        if User.objects.filter(username=manager_data['username']).exists():
            print(f"  ⚠ User '{manager_data['username']}' already exists, skipping...")
            continue
        # Create user
        user = User.objects.create_user(
            username=manager_data['username'],
            email=manager_data['email'],
            password=manager_data['password'],
            role=manager_data['role']
        )
        # Update the auto-created profile with test data
        profile = user.manager_profile
        for key, value in manager_data['profile'].items():
            setattr(profile, key, value)
        profile.save()
        print(f"  ✓ Created manager: {manager_data['username']} ({manager_data['profile']['club_name']}) - {manager_data['profile']['location_postcode']}")
    print(f"\n✅ Test manager data creation complete!")
    print(f"Total managers in database: {ManagerProfile.objects.count()}")

if __name__ == '__main__':
    create_test_managers()
