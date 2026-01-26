"""
Django management command to add clubs with RSS feeds (without user accounts).

Usage:
    python manage.py add_club "Club Name" "https://club-website.com/feed" --league "STEP_5" --postcode "SW1A 1AA"
"""
from django.core.management.base import BaseCommand
from users.models import ClubProfile


class Command(BaseCommand):
    help = 'Add a club with RSS feed URL to the database (without creating a user account)'

    def add_arguments(self, parser):
        parser.add_argument('club_name', type=str, help='Name of the club')
        parser.add_argument('rss_url', type=str, help='RSS feed URL')
        parser.add_argument(
            '--league',
            type=str,
            default='SUNDAY',
            help='League level (STEP_1 to STEP_7, SUNDAY, or OTHER)',
        )
        parser.add_argument(
            '--postcode',
            type=str,
            default='',
            help='Club postcode',
        )
        parser.add_argument(
            '--location',
            type=str,
            default='',
            help='City or region',
        )

    def handle(self, *args, **options):
        club_name = options['club_name']
        rss_url = options['rss_url']
        league_level = options['league']
        postcode = options['postcode']
        location = options['location']

        # Check if club already exists
        if ClubProfile.objects.filter(club_name=club_name).exists():
            self.stdout.write(
                self.style.WARNING(f'Club "{club_name}" already exists!')
            )
            return

        try:
            # Create club profile WITHOUT user account
            club_profile = ClubProfile.objects.create(
                club_name=club_name,
                rss_feed_url=rss_url,
                league_level=league_level,
                location_postcode=postcode,
                location=location,
                user=None,  # No user account
                is_registered=False
            )

            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully added club: {club_name}')
            )
            self.stdout.write(f'  RSS URL: {rss_url}')
            self.stdout.write(f'  League Level: {league_level}')
            self.stdout.write(f'  Type: Admin-added (no user account)')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error adding club: {str(e)}')
            )
