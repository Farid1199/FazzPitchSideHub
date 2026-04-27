import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# List ALL users
print("\nALL USERS IN DATABASE:")
print("="*60)
for user in User.objects.all():
    print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")

# Now delete all test users by username
test_usernames = [
    'gk_james', 'gk_david', 'lb_marcus', 'lb_andy', 'cb_john', 'cb_michael', 'cb_terry', 
    'rb_kyle', 'rb_trent', 'cdm_declan', 'cdm_casemiro', 'cm_kevin', 'cm_luka', 'cm_bruno',
    'cam_martin', 'cam_mason', 'lw_raheem', 'lw_jack', 'rw_mohamed', 'rw_bukayo',
    'st_harry', 'st_erling', 'st_victor', 'st_ivan', 'cf_robert', 'cf_darwin',
    'manager_alex', 'manager_jose', 'manager_pep', 'manager_jurgen', 'manager_emma', 'manager_steve'
]

deleted_count = 0
for username in test_usernames:
    try:
        user = User.objects.get(username=username)
        user.delete()
        deleted_count += 1
        print(f"Deleted: {username}")
    except User.DoesNotExist:
        pass

print(f"\nTotal deleted: {deleted_count}")
print(f"Remaining users: {User.objects.count()}")
