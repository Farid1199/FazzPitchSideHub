"""
Django management command to fetch RSS feeds from club sources.
Intelligent Scraper - Automatically categorizes content as News or Opportunities.

Features:
- Fetches RSS feeds from all ClubSource entries with configured RSS URLs
- Uses intelligent keyword detection to classify content:
  * Detects recruitment keywords (trial, recruiting, squad, etc.)
  * Detects position keywords (goalkeeper, defender, striker, midfielder, etc.)
  * Categorizes as Opportunity (trial) or NewsItem (regular news)
- Extracts target positions from content
- Prevents duplicate entries

Usage:
    python manage.py fetch_rss                    # Fetch from all club sources
    python manage.py fetch_rss --source-id 1     # Fetch from specific source
"""
import feedparser
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import ClubSource, NewsItem, Opportunity


class Command(BaseCommand):
    help = '''
    Intelligent RSS Feed Scraper - Fetches and categorizes club content from ClubSource entries
    - Automatically detects recruitment/trial opportunities vs regular news
    - Extracts position information (Goalkeeper, Defender, Striker, etc.)
    - Prevents duplicate entries
    - Filters out women's football, youth teams, and academy content
    '''
    
    # Exclusion keywords for data noise reduction (Hard Exclusion)
    EXCLUSION_KEYWORDS = [
        'women', 'ladies', 'girls', 'womens', "women's", 'lady', 'female',
        'u18', 'u17', 'u16', 'u15', 'u14', 'u13', 'u12', 'u11', 'u10', 'u9', 'u8',
        'u18s', 'u17s', 'u16s', 'u15s', 'u14s', 'u13s', 'u12s',  # Common variations
        'under 18', 'under 17', 'under 16', 'under-18', 'under-17', 'under-16',
        'youth', 'juniors', 'junior', 'academy', 'development', 'schoolboy',
        'boys', 'youth team', 'junior team', 'youth side'
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='Fetch RSS for a specific ClubSource ID only',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        source_id = options.get('source_id')
        
        # Display header
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('  🤖 INTELLIGENT RSS FEED SCRAPER'))
        self.stdout.write('=' * 70)
        self.stdout.write('  📡 Fetching feeds from club sources...')
        self.stdout.write('  🧠 Applying intelligence logic to categorize content')
        self.stdout.write('  🎯 Detecting: Trials, Recruitment, Positions')
        self.stdout.write('=' * 70 + '\n')
        
        # Get club sources with RSS feeds
        if source_id:
            sources = ClubSource.objects.filter(id=source_id, rss_url__isnull=False).exclude(rss_url='')
        else:
            sources = ClubSource.objects.filter(rss_url__isnull=False).exclude(rss_url='')
        
        if not sources.exists():
            self.stdout.write(self.style.WARNING('No club sources with RSS feeds found.'))
            return
        
        total_items = 0
        total_opportunities = 0
        
        for source in sources:
            self.stdout.write(f'\nProcessing RSS feed for: {source.name}')
            self.stdout.write(f'RSS URL: {source.rss_url}')
            
            try:
                # Parse the RSS feed
                feed = feedparser.parse(source.rss_url)
                
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
                    
                    # Apply exclusion filter (Data Noise Reduction)
                    if self._should_exclude(title, description):
                        self.stdout.write(f'  ⊗ Filtered (Youth/Women): {title[:50]}...')
                        continue
                    
                    # Check if this is a trial/recruitment opportunity
                    is_opportunity = self._is_opportunity(title, description)
                    
                    if is_opportunity:
                        # Save as Opportunity
                        opportunity, created = Opportunity.objects.get_or_create(
                            link=link,
                            defaults={
                                'source': source,
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
                            link=link,
                            defaults={
                                'source': source,
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
        self.stdout.write('\n' + '='*70)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ RSS Feed Fetch Complete!\n'
                f'   Total News Items: {total_items}\n'
                f'   Total Opportunities (Trials/Recruitment): {total_opportunities}\n'
                f'   Club Sources Processed: {sources.count()}'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n💡 Intelligence Logic Applied:\n'
                '   - Opportunities detected using recruitment keywords\n'
                '   - Position extraction from content\n'
                '   - Duplicate prevention active'
            )
        )
        self.stdout.write('='*70)

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
    
    def _should_exclude(self, title, description):
        """
        Check if content should be excluded based on exclusion keywords.
        Data Noise Reduction: Filters out women's football, youth teams, academy content.
        Returns True if content should be excluded.
        """
        combined_text = (title + ' ' + description).lower()
        
        # Check if any exclusion keyword appears in the text
        return any(keyword in combined_text for keyword in self.EXCLUSION_KEYWORDS)

    def _is_opportunity(self, title, description):
        """
        Check if a news item is a trial/recruitment opportunity.
        Strict Intelligence Logic: 
        - MUST contain trial/recruiting/vacancy/wanted/looking for keywords
        - MUST NOT contain signing/signed/joins/welcome/captured (these are announcements, not opportunities)
        """
        combined_text = (title + ' ' + description).lower()
        
        # Strict recruitment keywords (MUST have at least one)
        strict_recruitment_keywords = [
            'trial', 'trials', 'recruit', 'recruitment', 'recruiting', 
            'tryout', 'tryouts', 'vacancy', 'vacancies', 'wanted',
            'looking for', 'seeking players', 'seeking player',
            'apply now', 'applications open', 'register for trial'
        ]
        
        # Announcement keywords (if present, it's NOT an opportunity)
        announcement_keywords = [
            'signing', 'signed', 'signs', 'joins', 'joined', 'welcome',
            'captured', 'announces', 'announced', 'confirms', 'confirmed',
            'new signing', 'completes move', 'agrees deal'
        ]
        
        # Check for announcement keywords first (immediate disqualification)
        has_announcement = any(keyword in combined_text for keyword in announcement_keywords)
        if has_announcement:
            return False
        
        # Check for strict recruitment keywords
        has_recruitment = any(keyword in combined_text for keyword in strict_recruitment_keywords)
        
        return has_recruitment

    def _extract_position(self, title, description):
        """
        Extract target position from title or description.
        Enhanced to detect all major football positions.
        Only extracts player positions - ignores managerial/coaching roles.
        """
        combined_text = (title + ' ' + description).lower()
        
        # Check if this is a staff/managerial role (not a player opportunity)
        staff_keywords = [
            'manager', 'coach', 'assistant manager', 'head coach',
            'physiotherapist', 'physio', 'kit man', 'groundsman',
            'volunteer', 'administrator', 'secretary', 'treasurer',
            'committee', 'director', 'chairman', 'staff'
        ]
        
        if any(keyword in combined_text for keyword in staff_keywords):
            # This is a staff role, not a player position
            return ''
        
        # Define position keywords with variations
        positions = {
            'goalkeeper': ['goalkeeper', 'keeper', 'gk', 'goalie'],
            'defender': ['defender', 'defence', 'center back', 'centre back', 'cb', 'full back', 'fb'],
            'left back': ['left back', 'lb', 'left-back'],
            'right back': ['right back', 'rb', 'right-back'],
            'midfielder': ['midfielder', 'midfield', 'cm', 'central midfielder'],
            'defensive midfielder': ['defensive midfielder', 'cdm', 'holding midfielder'],
            'attacking midfielder': ['attacking midfielder', 'cam', 'playmaker'],
            'winger': ['winger', 'wing', 'wide player', 'lw', 'rw'],
            'striker': ['striker', 'forward', 'st', 'cf', 'center forward', 'centre forward'],
        }
        
        found_positions = []
        
        for position_name, variations in positions.items():
            if any(variation in combined_text for variation in variations):
                if position_name not in found_positions:
                    found_positions.append(position_name)
        
        # Return formatted positions
        return ', '.join([pos.title() for pos in found_positions]) if found_positions else ''
