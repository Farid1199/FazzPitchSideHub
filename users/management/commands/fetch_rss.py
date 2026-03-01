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
        self.stdout.write(self.style.SUCCESS('    INTELLIGENT RSS FEED SCRAPER'))
        self.stdout.write('=' * 70)
        self.stdout.write('    Fetching feeds from club sources...')
        self.stdout.write('    Applying intelligence logic to categorize content')
        self.stdout.write('    Detecting: Trials, Recruitment, Positions')
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
                    import html
                    from django.utils.html import strip_tags

                    # Extract entry data, strip tags and unescape HTML entities out of the text
                    raw_title = entry.get('title', 'No Title')
                    title = html.unescape(strip_tags(raw_title))
                    
                    link = entry.get('link', '')
                    
                    raw_description = entry.get('description', '') or entry.get('summary', '')
                    description = html.unescape(strip_tags(raw_description))
                    
                    # Parse published date
                    published_date = self._parse_date(entry)
                    
                    if not link:
                        self.stdout.write(self.style.WARNING(f'  Skipping entry without link: {title}'))
                        continue
                    
                    # Apply exclusion filter (Data Noise Reduction)
                    if self._should_exclude(title, description):
                        self.stdout.write(f'  [FILTERED] (Youth/Women): {title[:50]}...')
                        continue
                    
                    # Check if this is a trial/recruitment opportunity
                    is_opportunity = self._is_opportunity(title, description)
                    
                    from thefuzz import fuzz
                    
                    if is_opportunity:
                        # Fuzzy Deduplication (Levenshtein Distance)
                        # Check if a very similar opportunity already exists for this source
                        is_duplicate = False
                        recent_opps = Opportunity.objects.filter(
                            source=source, 
                            is_open=True
                        ).order_by('-published_date')[:50]
                        
                        for existing_opp in recent_opps:
                            # token_set_ratio is great for varied wording but same keywords
                            similarity = fuzz.token_set_ratio(title.lower(), existing_opp.title.lower())
                            if similarity > 90:
                                self.stdout.write(self.style.WARNING(f'  [DUPLICATE] trial ({similarity}% match): {title[:40]}...'))
                                is_duplicate = True
                                break
                                
                        if is_duplicate:
                            continue
                            
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
                                self.style.SUCCESS(f'  [ADDED] Opportunity: {title[:60]}...')
                            )
                    else:
                        # Fuzzy Deduplication for General News
                        is_duplicate = False
                        
                        # Only check against generic NewsItems, not Opportunities
                        opportunity_ids = Opportunity.objects.filter(source=source).values_list('newsitem_ptr_id', flat=True)
                        recent_news = NewsItem.objects.filter(
                            source=source
                        ).exclude(
                            id__in=opportunity_ids
                        ).order_by('-published_date')[:50]
                        
                        for existing_news in recent_news:
                            similarity = fuzz.token_set_ratio(title.lower(), existing_news.title.lower())
                            if similarity > 90:
                                self.stdout.write(self.style.WARNING(f'  [DUPLICATE] news ({similarity}% match): {title[:40]}...'))
                                is_duplicate = True
                                break
                                
                        if is_duplicate:
                            continue
                            
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
                            self.stdout.write(f'  [ADDED] NewsItem: {title[:60]}...')
                
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
                f'   RSS Feed Fetch Complete!\n'
                f'   Total News Items: {total_items}\n'
                f'   Total Opportunities (Trials/Recruitment): {total_opportunities}\n'
                f'   Club Sources Processed: {sources.count()}'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n   Intelligence Logic Applied:\n'
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
        First attempts to use Google Generative AI (Gemini) for highly accurate extraction.
        If the API fails or is not configured, falls back to Regex matching.
        """
        import re
        import json
        from django.utils.html import strip_tags
        from django.conf import settings
        
        clean_title = strip_tags(title)
        clean_desc = strip_tags(description)
        combined_text = (clean_title + ' ' + clean_desc).strip()
        
        # AI-Powered LLM Parsing (Gemini)
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Using gemini-1.5-flash which is extremely fast and cheap
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                You are a smart football/soccer data extractor. Read the following text from a club's recruitment post.
                Determine the specific player position(s) they are recruiting for.
                If this is a staff, managerial, medical, volunteer, or coaching role (NOT a playing role), return "is_staff_role": true.
                If it is a player role, return standard position names (e.g., "Goalkeeper", "Striker", "Center Back").
                Return ONLY a strict JSON object with no markdown formatting.
                
                Text to analyze:
                {combined_text[:500]}
                
                Required JSON format:
                {{
                    "is_staff_role": <boolean>,
                    "positions": ["<Position 1>", "<Position 2>"]
                }}
                """
                
                response = model.generate_content(prompt)
                
                # Strip potential markdown backticks from response
                raw_json = response.text.strip().removeprefix('```json').removesuffix('```').strip()
                result = json.loads(raw_json)
                
                if result.get("is_staff_role", False):
                    self.stdout.write(self.style.WARNING("    [GEMINI] Detected non-player staff role. Discarding position."))
                    return ''
                
                extracted_positions = result.get("positions", [])
                if extracted_positions:
                    valid_positions = [pos.title() for pos in extracted_positions if pos]
                    if valid_positions:
                        self.stdout.write(self.style.SUCCESS(f"    [GEMINI] Accurately extracted: {', '.join(valid_positions)}"))
                        return ', '.join(valid_positions)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    [GEMINI ERROR] {str(e)}. Falling back to Regex..."))
                
        # Regex Fallback (If Gemini is disabled or fails)
        combined_text_lower = combined_text.lower()
        import re
        from django.utils.html import strip_tags
        
        # Strip HTML tags before searching to avoid matching inside URLs/attributes
        clean_title = strip_tags(title)
        clean_desc = strip_tags(description)
        combined_text = (clean_title + ' ' + clean_desc).lower()
        
        # Check if this is a staff/managerial role (not a player opportunity)
        staff_keywords = [
            'manager', 'coach', 'assistant manager', 'head coach',
            'physiotherapist', 'physio', 'kit man', 'groundsman',
            'volunteer', 'administrator', 'secretary', 'treasurer',
            'committee', 'director', 'chairman', 'staff',
            'therapist', 'therapy', 'medical', 'student vacancy'
        ]
        
        # Use regex word boundaries for staff keywords too
        for keyword in staff_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', combined_text_lower):
                return ''
        
        # Define positions and their regex patterns (using \b for word boundaries)
        positions = {
            'goalkeeper': [r'\bgoalkeeper\b', r'\bkeeper\b', r'\bgk\b', r'\bgoalie\b'],
            'defender': [r'\bdefender\b', r'\bdefence\b', r'\bcenter back\b', r'\bcentre back\b', r'\bcb\b', r'\bfull back\b', r'\bfb\b'],
            'left back': [r'\bleft back\b', r'\blb\b', r'\bleft-back\b'],
            'right back': [r'\bright back\b', r'\brb\b', r'\bright-back\b'],
            'midfielder': [r'\bmidfielder\b', r'\bmidfield\b', r'\bcm\b', r'\bcentral midfielder\b'],
            'defensive midfielder': [r'\bdefensive midfielder\b', r'\bcdm\b', r'\bholding midfielder\b'],
            'attacking midfielder': [r'\battacking midfielder\b', r'\bcam\b', r'\bplaymaker\b'],
            'winger': [r'\bwinger\b', r'\bwing\b', r'\bwide player\b', r'\blw\b', r'\brw\b'],
            'striker': [r'\bstriker\b', r'\bforward\b', r'\bst\b', r'\bcf\b', r'\bcenter forward\b', r'\bcentre forward\b'],
        }
        
        found_positions = []
        
        for position_name, patterns in positions.items():
            for pattern in patterns:
                if re.search(pattern, combined_text_lower):
                    if position_name not in found_positions:
                        found_positions.append(position_name)
                    break # Stop checking patterns for this position if we found a match
        
        # Return formatted positions
        return ', '.join([pos.title() for pos in found_positions]) if found_positions else ''
