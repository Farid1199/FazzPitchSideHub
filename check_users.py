import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, PlayerProfile, ManagerProfile

# Check all users
all_users = User.objects.all()
print(f'\nTotal users in database: {all_users.count()}')

# Check players
players = User.objects.filter(role='PLAYER')
print(f'Total PLAYER role users: {players.count()}')
print(f'Total PlayerProfile objects: {PlayerProfile.objects.count()}')

# Show test users
test_patterns = ['gk_', 'lb_', 'cb_', 'rb_', 'cdm_', 'cm_', 'cam_', 'lw_', 'rw_', 'st_', 'cf_', 'manager_']
for pattern in test_patterns:
    users = User.objects.filter(username__startswith=pattern)
    if users.exists():
        print(f'\n{pattern}* users:')
        for u in users:
            try:
                if u.role == 'PLAYER':
                    profile = u.player_profile
                    print(f'  {u.username}: {profile.position} ({profile.get_position_display()})')
                else:
                    profile = u.manager_profile
                    print(f'  {u.username}: Manager')
            except:
                print(f'  {u.username}: NO PROFILE!')
