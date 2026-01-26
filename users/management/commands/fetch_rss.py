"""
Django management command to fetch RSS feeds from clubs.

Usage:
    python manage.py fetch_rss
"""
import feedparser
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import ClubProfile, NewsItem, Opportunity


class Command(BaseCommand):
    help = 'Fetches RSS feeds from all clubs with RSS URLs and saves news items and opportunities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--club-id',
            type=int,
            help='Fetch RSS for a specific club ID only',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        club_id = options.get('club_id')
        
        # Get clubs with RSS feeds
        if club_id:
            clubs = ClubProfile.objects.filter(id=club_id, rss_feed_url__isnull=False).exclude(rss_feed_url='')
        else:
            clubs = ClubProfile.objects.filter(rss_feed_url__isnull=False).exclude(rss_feed_url='')
        
        if not clubs.exists():
            self.stdout.write(self.style.WARNING('No clubs with RSS feeds found.'))
            return
        
        total_items = 0
        total_opportunities = 0
        
        for club in clubs:
            self.stdout.write(f'\nProcessing RSS feed for: {club.club_name}')
            self.stdout.write(f'RSS URL: {club.rss_feed_url}')
            
            try:
                # Parse the RSS feed
                feed = feedparser.parse(club.rss_feed_url)
                
                if feed.bozo:
                    # Feed has errors
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Warning: Feed may have parsing issues: {getattr(feed, "bozo_exception", "Unknown error")}'
                        )
                    )
                
                if not feed.entries:
                    self.stdout.write(self.style.WARNING('  No entries found in feed.'))
                    continue
                
                items_added = 0
                opportunities_added = 0
                
                for entry in feed.entries:
                    # Extract entry data
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    description = entry.get('description', '') or entry.get('summary', '')
                    
                    # Parse published date
                    published_date = self._parse_date(entry)
                    
                    if not link:
                        self.stdout.write(self.style.WARNING(f'  Skipping entry without link: {title}'))
                        continue
                    
                    # Check if this is a trial/recruitment opportunity
                    is_opportunity = self._is_opportunity(title, description)
                    
                    if is_opportunity:
                        # Save as Opportunity
                        opportunity, created = Opportunity.objects.get_or_create(
                            club=club,
                            link=link,
                            defaults={
                                'title': title,
                                'description': description,
                                'published_date': published_date,
                                'target_position': self._extract_position(title, description),
                                'is_open': True,
                            }
                        )
                        
                        if created:
                            opportunities_added += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ Added Opportunity: {title[:60]}...')
                            )
                    else:
                        # Save as NewsItem
                        news_item, created = NewsItem.objects.get_or_create(
                            club=club,
                            link=link,
                            defaults={
                                'title': title,
                                'description': description,
                                'published_date': published_date,
                            }
                        )
                        
                        if created:
                            items_added += 1
                            self.stdout.write(f'  ✓ Added NewsItem: {title[:60]}...')
                
                total_items += items_added
                total_opportunities += opportunities_added
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Summary: {items_added} news items, {opportunities_added} opportunities added'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error processing feed: {str(e)}')
                )
        
        # Final summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Total: {total_items} news items and {total_opportunities} opportunities added'
            )
        )

    def _parse_date(self, entry):
        """Parse the published date from an RSS entry"""
        # Try different date fields
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    dt = datetime(*time_struct[:6])
                    # Make timezone-aware
                    return timezone.make_aware(dt, timezone.get_current_timezone())
                except Exception:
                    continue
        
        # If no date found, use current time
        return timezone.now()

    def _is_opportunity(self, title, description):
        """Check if a news item is a trial/recruitment opportunity"""
        keywords = ['trial', 'trials', 'recruit', 'recruitment', 'recruiting', 
                    'tryout', 'tryouts', 'vacancy', 'vacancies', 'wanted',
                    'looking for', 'seeking players']
        
        combined_text = (title + ' ' + description).lower()
        
        return any(keyword in combined_text for keyword in keywords)

    def _extract_position(self, title, description):
        """Attempt to extract target position from title or description"""
        positions = [
            'goalkeeper', 'defender', 'midfielder', 'striker', 'forward',
            'winger', 'centre back', 'full back', 'attacking', 'defensive'
        ]
        
        combined_text = (title + ' ' + description).lower()
        
        found_positions = [pos for pos in positions if pos in combined_text]
        
        return ', '.join(found_positions).title() if found_positions else ''
