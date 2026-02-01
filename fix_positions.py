"""
Fixed script to update existing player positions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, PlayerProfile

# Update existing players with correct positions
position_mapping = {
    'player': 'CF',  # Keep existing players
    'player2': 'CM',
}

# Update existing test players if they exist
updates = [
    ('gk_james', 'GK'),
    ('gk_david', 'GK'),
    ('lb_marcus', 'LB'),
    ('lb_andy', 'LB'),
    ('cb_john', 'CB'),
    ('cb_michael', 'CB'),
    ('cb_terry', 'CB'),
    ('rb_kyle', 'RB'),
    ('rb_trent', 'RB'),
    ('cdm_declan', 'CDM'),
    ('cdm_casemiro', 'CDM'),
    ('cm_kevin', 'CM'),
    ('cm_luka', 'CM'),
    ('cm_bruno', 'CM'),
    ('cam_martin', 'CAM'),
    ('cam_mason', 'CAM'),
    ('lw_raheem', 'LW'),
    ('lw_jack', 'LW'),
    ('rw_mohamed', 'RW'),
    ('rw_bukayo', 'RW'),
    ('st_harry', 'ST'),
    ('st_erling', 'ST'),
    ('st_victor', 'ST'),
    ('st_ivan', 'ST'),
    ('cf_robert', 'CF'),
    ('cf_darwin', 'CF'),
]

print("Updating existing players...")
for username, new_position in position_mapping.items():
    try:
        user = User.objects.get(username=username)
        profile = user.player_profile
        profile.position = new_position
        profile.save()
        print(f"✅ Updated {username} to {new_position}")
    except:
        print(f"❌ Skipped {username} (not found or no profile)")

print(f"\nDone! Updated {len(position_mapping)} players")
