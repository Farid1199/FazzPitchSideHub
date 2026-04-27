import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubProfile


def main():
    print('=' * 60)
    print('TESTING CLUB SEARCH FEATURE')
    print('=' * 60)

    print(f'\nTotal clubs in database: {ClubProfile.objects.count()}')

    print('\n1. Searching by name "City":')
    results = ClubProfile.objects.filter(club_name__icontains='City')
    print(f'Found {results.count()} clubs:')
    for club in results:
        print(f'  - {club.club_name} ({club.location})')

    print('\n2. Searching by level "SUNDAY":')
    results = ClubProfile.objects.filter(league_level='SUNDAY')
    print(f'Found {results.count()} clubs:')
    for club in results:
        print(f'  - {club.club_name} ({club.get_league_level_display()})')

    print('\n3. Searching by location "London":')
    results = ClubProfile.objects.filter(location__icontains='London')
    print(f'Found {results.count()} clubs:')
    for club in results:
        print(f'  - {club.club_name}')

    print('\n4. Searching by postcode starting with "M":')
    results = ClubProfile.objects.filter(location_postcode__istartswith='M')
    print(f'Found {results.count()} clubs:')
    for club in results:
        print(f'  - {club.club_name} ({club.location_postcode})')

    print('\n5. Combined search - Level: STEP_5, League contains "League":')
    results = ClubProfile.objects.filter(
        league_level='STEP_5',
        league__icontains='League'
    )
    print(f'Found {results.count()} clubs:')
    for club in results:
        print(f'  - {club.club_name} ({club.league})')

    print('\n' + '=' * 60)


if __name__ == '__main__':
    main()
