import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import PlayerProfile
from django.db.models import Count

print('=' * 60)
print('PLAYER SEARCH DIAGNOSTICS')
print('=' * 60)

print(f'\nTotal players in database: {PlayerProfile.objects.count()}')
print(f'Available players: {PlayerProfile.objects.filter(available_for_club=True).count()}')

print('\nPlayers by position:')
result = PlayerProfile.objects.values('position').annotate(count=Count('position')).order_by('position')
for r in result:
    print(f'  {r["position"]}: {r["count"]}')

print('\nTesting position filter (GK):')
gks = PlayerProfile.objects.filter(position='GK', available_for_club=True)
print(f'Found {gks.count()} available goalkeepers:')
for gk in gks:
    print(f'  - {gk.user.username} (Available: {gk.available_for_club})')

print('\nTesting level filter (STEP_5):')
step5_players = PlayerProfile.objects.filter(playing_level='STEP_5', available_for_club=True)
print(f'Found {step5_players.count()} Step 5 players:')
for player in step5_players[:5]:
    print(f'  - {player.user.username} ({player.position})')

print('\nTesting postcode filter (M1):')
m1_players = PlayerProfile.objects.filter(location_postcode__istartswith='M1', available_for_club=True)
print(f'Found {m1_players.count()} players in M1 area:')
for player in m1_players:
    print(f'  - {player.user.username} ({player.location_postcode})')

print('\n' + '=' * 60)
