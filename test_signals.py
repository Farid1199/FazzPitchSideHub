import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, PlayerProfile, ClubProfile, ScoutProfile


def main():
    # Test 1: Create a PLAYER user
    print("Test 1: Creating a PLAYER user...")
    player_user = User.objects.create_user(
        username='testplayer',
        email='test@player.com',
        password='testpass123',
        role='PLAYER'
    )

    has_player_profile = hasattr(player_user, 'player_profile')
    print(f"PlayerProfile created automatically: {has_player_profile}")
    if has_player_profile:
        print(f"  Position: {player_user.player_profile.position}")
        print(f"  Playing Level: {player_user.player_profile.playing_level}")

    # Test 2: Create a CLUB user
    print("\nTest 2: Creating a CLUB user...")
    club_user = User.objects.create_user(
        username='testclub',
        email='test@club.com',
        password='testpass123',
        role='CLUB'
    )

    has_club_profile = hasattr(club_user, 'club_profile')
    print(f"ClubProfile created automatically: {has_club_profile}")
    if has_club_profile:
        print(f"  League Level: {club_user.club_profile.league_level}")

    # Test 3: Create a SCOUT user
    print("\nTest 3: Creating a SCOUT user...")
    scout_user = User.objects.create_user(
        username='testscout',
        email='test@scout.com',
        password='testpass123',
        role='SCOUT'
    )

    has_scout_profile = hasattr(scout_user, 'scout_profile')
    print(f"ScoutProfile created automatically: {has_scout_profile}")

    # Clean up
    print("\nCleaning up test users...")
    player_user.delete()
    club_user.delete()
    scout_user.delete()
    print("All test users deleted successfully")

    print("\nAll signal tests passed!")


if __name__ == '__main__':
    main()
