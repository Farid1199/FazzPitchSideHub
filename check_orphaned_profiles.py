import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, PlayerProfile, ManagerProfile

# Check for orphaned profiles
print("\nCHECKING FOR ORPHANED PROFILES:")
print("="*60)

all_profiles = PlayerProfile.objects.all()
print(f"Total PlayerProfile objects: {all_profiles.count()}")

for profile in all_profiles:
    try:
        user = profile.user
        print(f"Profile ID {profile.id} -> User: {user.username} (ID: {user.id}), Position: {profile.position}")
    except:
        print(f"Profile ID {profile.id} -> ORPHANED! (user_id: {profile.user_id})")

print("\n" + "="*60)

all_manager_profiles = ManagerProfile.objects.all()
print(f"Total ManagerProfile objects: {all_manager_profiles.count()}")

for profile in all_manager_profiles:
    try:
        user = profile.user
        print(f"Profile ID {profile.id} -> User: {user.username} (ID: {user.id})")
    except:
        print(f"Profile ID {profile.id} -> ORPHANED! (user_id: {profile.user_id})")
