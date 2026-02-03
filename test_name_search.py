import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import PlayerProfile

print('=' * 60)
print('TESTING NAME SEARCH FEATURE')
print('=' * 60)

# Test partial name search
print('\nSearching for "james":')
results = PlayerProfile.objects.filter(user__username__icontains='james', available_for_club=True)
print(f'Found {results.count()} players:')
for player in results:
    print(f'  - {player.user.username} ({player.position})')

print('\nSearching for "gk":')
results = PlayerProfile.objects.filter(user__username__icontains='gk', available_for_club=True)
print(f'Found {results.count()} players:')
for player in results:
    print(f'  - {player.user.username} ({player.position})')

print('\nSearching for "cm_":')
results = PlayerProfile.objects.filter(user__username__icontains='cm_', available_for_club=True)
print(f'Found {results.count()} players:')
for player in results:
    print(f'  - {player.user.username} ({player.position})')

print('\nCombined search - Position: GK, Name: "david":')
results = PlayerProfile.objects.filter(
    position='GK',
    user__username__icontains='david',
    available_for_club=True
)
print(f'Found {results.count()} players:')
for player in results:
    print(f'  - {player.user.username} ({player.position})')

print('\n' + '=' * 60)
