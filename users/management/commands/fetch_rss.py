"""
Django management command to fetch RSS feeds from club sources.
Multi-Layer Intelligent Scraper with 3 classification tiers:

Tier 1 — Regex Detection (free, instant):
    • Match Reports: Detects scoreline patterns (e.g. '2-1', '0 - 0')
    • Transfer News: Detects signing/departure language
    • Explicit Trials: Detects exact trial/recruitment keywords

Tier 2 — Gemini AI Intent Scoring (contextual understanding):
    • Scores every non-categorized article 0-100 for recruitment intent
    • Catches subtle signals like 'looking to strengthen the squad'
    • Saves reasoning as ai_summary for transparency

Tier 3 — Fallback:
    • Anything not caught by Tier 1 or 2 → General News

Usage:
    python manage.py fetch_rss                    # Fetch from all club sources
    python manage.py fetch_rss --source-id 1     # Fetch from specific source
    python manage.py fetch_rss --no-ai           # Skip Gemini (regex only)
"""
import re
import json
import html
import feedparser
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from users.models import ClubSource, NewsItem, Opportunity


class Command(BaseCommand):
    help = '''
    Multi-Layer Intelligent RSS Feed Scraper
    
    Classification Pipeline:
    ┌─────────────────────────────────────────────────────┐
    │ Layer 1: Hard Exclusion (youth/women's content)     │
    │ Layer 2: Strict Keyword → Confirmed Trial           │
    │ Layer 3: Regex Patterns → Match Report / Transfer   │
    │ Layer 4: Gemini AI → Recruitment Signal (score 0-100)│
    │ Layer 5: Fallback → General News                    │
    └─────────────────────────────────────────────────────┘
    '''
    
    # ── Hard Exclusion Keywords (Data Noise Reduction) ──
    EXCLUSION_KEYWORDS = [
        'women', 'ladies', 'girls', 'womens', "women's", 'lady', 'female',
        'u18', 'u17', 'u16', 'u15', 'u14', 'u13', 'u12', 'u11', 'u10', 'u9', 'u8',
        'u18s', 'u17s', 'u16s', 'u15s', 'u14s', 'u13s', 'u12s',
        'under 18', 'under 17', 'under 16', 'under-18', 'under-17', 'under-16',
        'youth', 'juniors', 'junior', 'academy', 'development', 'schoolboy',
        'boys', 'youth team', 'junior team', 'youth side'
    ]

    # ── Regex: Scoreline pattern for Match Reports ──
    # Matches: "2-1", "3 - 0", "0-0", also "2 -1" etc.
    SCORELINE_REGEX = re.compile(r'\b\d{1,2}\s*[-–—]\s*\d{1,2}\b')
    
    # Matches: "Club A vs Club B", "Club A v Club B" in titles
    VS_PATTERN = re.compile(r'\b(?:vs?\.?\s)', re.IGNORECASE)
    
    # Additional match report context keywords (used alongside scoreline)
    MATCH_CONTEXT_KEYWORDS = [
        'match report', 'match preview', 'post-match', 'post match',
        'player ratings', 'man of the match', 'motm',
        'half time', 'half-time', 'full time', 'full-time',
        'fixture', 'result', 'goals', 'goal scored',
        'defeated', 'beat', 'drew', 'draw', 'victory', 'win ',
        'lost to', 'loss against', 'equaliser', 'penalty',
    ]
    
    # ── Transfer Detection: Strong Phrases (always trigger) ──
    STRONG_TRANSFER_PHRASES = [
        'new signing', 'loan signing', 'loan move', 'loan deal',
        'agrees terms', 'agreed terms', 'completes move',
        'signs contract', 'extends contract', 'new contract',
        'left the club', 'leaves the club', 'moving on',
        'welcome to the club', 'welcome aboard',
        'transfer window', 'retained list', 'release list',
        'new arrival', 'new addition', 'signs for',
        'joins the club', 'departs the club',
    ]
    
    # ── Transfer Detection: Weak Words (only trigger when no scoreline present) ──
    WEAK_TRANSFER_WORDS = [
        'signing', 'signed', 'departure', 'departures', 'departed',
        'on loan', 'released', 'retained', 'arrivals',
        'captures', 'joins', 'joined',
    ]
    
    # ── Strict Keywords for Confirmed Trials ──
    TRIAL_KEYWORDS = [
        'trial', 'trials', 'open trial', 'open trials',
        'recruit', 'recruitment', 'recruiting',
        'tryout', 'tryouts', 'try-out',
        'vacancy', 'vacancies', 'player wanted', 'players wanted',
        'looking for players', 'seeking players', 'seeking player',
        'apply now', 'applications open', 'register for trial',
        'come and trial', 'pre-season trial',
    ]
    
    # ── Anti-Trial Keywords (disqualify trial classification) ──
    ANNOUNCEMENT_KEYWORDS = [
        'signing', 'signed', 'signs', 'joins', 'joined', 'welcome',
        'captured', 'announces', 'announced', 'confirms', 'confirmed',
        'new signing', 'completes move', 'agrees deal',
        'recruited', 'appointed', 'named', 'hired',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='Fetch RSS for a specific ClubSource ID only',
        )
        parser.add_argument(
            '--no-ai',
            action='store_true',
            help='Skip Gemini AI scoring (use regex classification only)',
        )

    def _safe_write(self, msg, style_func=None):
        """Write to stdout with safe encoding (replaces unencodable chars)."""
        safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
        if style_func:
            self.stdout.write(style_func(safe_msg))
        else:
            self.stdout.write(safe_msg)

    def handle(self, *args, **options):
        """Main command handler — orchestrates the multi-layer classification pipeline."""
        source_id = options.get('source_id')
        skip_ai = options.get('no_ai', False)
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('    MULTI-LAYER INTELLIGENT RSS SCRAPER'))
        self.stdout.write('=' * 70)
        self.stdout.write('    Classification Pipeline:')
        self.stdout.write('    L1: Hard Exclusion -> L2: Trial Keywords')
        self.stdout.write('    L3: Regex (Match/Transfer) -> L4: Gemini AI Intent')
        self.stdout.write('    L5: Fallback -> General News')
        if skip_ai:
            self.stdout.write(self.style.WARNING('    [!] AI scoring DISABLED (--no-ai flag)'))
        self.stdout.write('=' * 70 + '\n')
        
        # Get club sources with RSS feeds
        if source_id:
            sources = ClubSource.objects.filter(id=source_id, rss_url__isnull=False).exclude(rss_url='')
        else:
            sources = ClubSource.objects.filter(rss_url__isnull=False).exclude(rss_url='')
        
        if not sources.exists():
            self.stdout.write(self.style.WARNING('No club sources with RSS feeds found.'))
            return
        
        stats = {'general': 0, 'trial': 0, 'transfer': 0, 'match': 0, 'recruitment_signal': 0, 'filtered': 0, 'duplicate': 0}
        
        for source in sources:
            self._safe_write(f'\n{"-"*50}')
            self._safe_write(f'  Source: {source.name}')
            self._safe_write(f'  RSS:    {source.rss_url}')
            
            try:
                feed = feedparser.parse(source.rss_url)
                
                if feed.bozo:
                    self._safe_write(
                        f'  Warning: Feed parsing issues: {getattr(feed, "bozo_exception", "Unknown")}',
                        self.style.WARNING
                    )
                
                if not feed.entries:
                    self._safe_write('  No entries found.', self.style.WARNING)
                    continue
                
                for entry in feed.entries:
                    raw_title = entry.get('title', 'No Title')
                    title = html.unescape(strip_tags(raw_title))
                    
                    link = entry.get('link', '')
                    
                    raw_description = entry.get('description', '') or entry.get('summary', '')
                    description = html.unescape(strip_tags(raw_description))
                    
                    published_date = self._parse_date(entry)
                    
                    if not link:
                        continue
                    
                    # ── LAYER 1: Hard Exclusion ──
                    if self._should_exclude(title, description):
                        self._safe_write(f'  [FILTERED] {title[:50]}...')
                        stats['filtered'] += 1
                        continue
                    
                    # ── Fuzzy Deduplication ──
                    if self._is_duplicate(title, source):
                        self._safe_write(f'  [DUPLICATE] {title[:45]}...', self.style.WARNING)
                        stats['duplicate'] += 1
                        continue
                    
                    # ── LAYER 2: Regex — Match Report Detection ──
                    if self._is_match_report(title, description):
                        self._save_news(source, title, link, description, published_date, category='match')
                        self._safe_write(f'  [MATCH]  {title[:55]}...')
                        stats['match'] += 1
                        continue
                    
                    # ── LAYER 3: Strict Trial Keywords ──
                    if self._is_confirmed_trial(title, description):
                        self._save_opportunity(
                            source, title, link, description, published_date,
                            category='trial', ai_score=0, ai_reason=''
                        )
                        self._safe_write(f'  [TRIAL] {title[:55]}...', self.style.SUCCESS)
                        stats['trial'] += 1
                        continue
                    
                    # ── LAYER 3b: Regex — Transfer Detection ──
                    if self._is_transfer(title, description):
                        self._save_news(source, title, link, description, published_date, category='transfer')
                        self._safe_write(f'  [TRANSFER] {title[:52]}...')
                        stats['transfer'] += 1
                        continue
                    
                    # ── LAYER 4: Gemini AI Recruitment Intent Scoring ──
                    if not skip_ai:
                        ai_result = self._analyze_recruitment_intent(title, description)
                        if ai_result and ai_result['score'] > 70:
                            self._save_opportunity(
                                source, title, link, description, published_date,
                                category='recruitment_signal',
                                ai_score=ai_result['score'],
                                ai_reason=ai_result['reason']
                            )
                            self._safe_write(
                                f'  [AI SIGNAL {ai_result["score"]}%] {title[:45]}...',
                                self.style.SUCCESS
                            )
                            self._safe_write(f'    Reason: {ai_result["reason"][:70]}')
                            stats['recruitment_signal'] += 1
                            continue
                    
                    # ── LAYER 5: Fallback -> General News ──
                    self._save_news(source, title, link, description, published_date, category='general')
                    stats['general'] += 1
                
            except Exception as e:
                self._safe_write(f'  Error: {str(e)}', self.style.ERROR)
        
        # ── Final Summary ──
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('    SCRAPE COMPLETE -- Classification Summary'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'    Confirmed Trials:      {stats["trial"]}')
        self.stdout.write(f'    Recruitment Signals:    {stats["recruitment_signal"]}')
        self.stdout.write(f'    Transfer News:          {stats["transfer"]}')
        self.stdout.write(f'    Match Reports:          {stats["match"]}')
        self.stdout.write(f'    General News:           {stats["general"]}')
        self.stdout.write(f'    Filtered (exclusion):   {stats["filtered"]}')
        self.stdout.write(f'    Duplicates skipped:     {stats["duplicate"]}')
        self.stdout.write(f'    Sources processed:      {sources.count()}')
        self.stdout.write('=' * 70)

    # ═══════════════════════════════════════════════════════
    #  DETECTION METHODS
    # ═══════════════════════════════════════════════════════

    def _should_exclude(self, title, description):
        """Layer 1: Hard exclusion for women's, youth, and academy content."""
        combined = (title + ' ' + description).lower()
        return any(kw in combined for kw in self.EXCLUSION_KEYWORDS)

    def _is_confirmed_trial(self, title, description):
        """
        Layer 2: Strict keyword detection for confirmed trials.
        MUST contain trial/recruitment language.
        MUST NOT contain announcement language (signing/joins/welcome).
        """
        combined = (title + ' ' + description).lower()
        
        if any(kw in combined for kw in self.ANNOUNCEMENT_KEYWORDS):
            return False
        
        return any(kw in combined for kw in self.TRIAL_KEYWORDS)

    def _is_match_report(self, title, description):
        """
        Layer 3a: Regex-based match report detection.
        Primary signal: scoreline pattern in title (e.g., '2-1', '3 - 0').
        Secondary signal: match context keywords in title or description.
        
        Reasoning: Scorelines in titles are an extremely reliable indicator
        of match reports — clubs almost always format headlines as 
        'Club A 2-1 Club B' or 'Match Report: 2-1 victory'.
        """
        title_lower = title.lower()
        combined = (title + ' ' + description).lower()
        
        # Primary: scoreline in title is strong evidence
        if self.SCORELINE_REGEX.search(title):
            return True
        
        # Secondary: scoreline in description + match context keyword in title
        if self.SCORELINE_REGEX.search(description):
            if any(kw in title_lower for kw in self.MATCH_CONTEXT_KEYWORDS):
                return True
        
        # Tertiary: explicit match report language in title
        explicit_match_phrases = ['match report', 'post-match', 'post match', 'player ratings', 'match preview', 'pre-match preview', 'recap:']
        if any(phrase in title_lower for phrase in explicit_match_phrases):
            return True
        
        # Quaternary: "vs" / "v" pattern in title with scoreline in description
        if self.VS_PATTERN.search(title) and self.SCORELINE_REGEX.search(description):
            return True
        
        return False

    def _is_transfer(self, title, description):
        """
        Layer 3b: Transfer news detection with disambiguation.
        
        Uses a 2-tier approach:
        - Strong phrases always trigger (e.g. 'new signing', 'loan move')
        - Weak words only trigger when NO scoreline in title/description
          (prevents match reports about loan players being miscategorised)
        """
        title_lower = title.lower()
        combined = (title + ' ' + description).lower()
        
        # Strong phrases in title → always trigger
        if any(phrase in title_lower for phrase in self.STRONG_TRANSFER_PHRASES):
            return True
        
        # Weak words in title → only if no scoreline present (disambiguation)
        has_scoreline = bool(self.SCORELINE_REGEX.search(title + ' ' + description))
        if not has_scoreline:
            if any(word in title_lower for word in self.WEAK_TRANSFER_WORDS):
                return True
        
        # Strong phrases in description → trigger
        desc_lower = description.lower()
        return any(phrase in desc_lower for phrase in self.STRONG_TRANSFER_PHRASES)

    def _analyze_recruitment_intent(self, title, description):
        """
        Layer 4: Gemini AI recruitment intent scoring.
        
        Sends the article to Google Gemini and asks it to score 0-100 
        for recruitment likelihood. This catches the subtle signals that
        keyword matching misses, e.g.:
        - 'Looking to strengthen the squad ahead of the new season'
        - 'Several positions remain unfilled'
        - 'Manager keen to add depth in midfield'
        
        Returns: dict with 'score' (int) and 'reason' (str), or None on failure.
        """
        from django.conf import settings
        
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            return None
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            combined_text = f"{title}. {description}"[:800]
            
            prompt = f"""Analyze this non-league football news article. Score it from 0 to 100 based 
on the likelihood that the club is actively recruiting, looking for new players, or hosting open trials.

Scoring guide:
- 90-100: Explicit trial or recruitment announcement
- 70-89: Strong signals of recruitment need (squad gaps, departures, manager wanting to add players)
- 40-69: Mild hints but nothing concrete
- 0-39: No recruitment intent (match reports, sponsorship, community events)

Article title: {title}
Article content: {description[:600]}

Return ONLY a JSON object, no markdown:
{{"score": <integer 0-100>, "reason": "<1 sentence explanation>"}}"""

            response = model.generate_content(prompt)
            raw = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            result = json.loads(raw)
            
            score = int(result.get('score', 0))
            reason = str(result.get('reason', ''))[:300]
            
            return {'score': score, 'reason': reason}
            
        except Exception as e:
            self._safe_write(f'    [AI ERROR] {str(e)}', self.style.ERROR)
            return None

    # ═══════════════════════════════════════════════════════
    #  SAVE METHODS
    # ═══════════════════════════════════════════════════════

    def _save_opportunity(self, source, title, link, description, published_date,
                          category, ai_score, ai_reason):
        """Save as Opportunity (trial or recruitment signal)."""
        try:
            Opportunity.objects.get_or_create(
                link=link,
                defaults={
                    'source': source,
                    'title': title,
                    'description': description,
                    'published_date': published_date,
                    'category': category,
                    'target_position': self._extract_position(title, description),
                    'is_open': True,
                    'ai_recruitment_score': ai_score,
                    'ai_summary': ai_reason,
                }
            )
        except Exception as e:
            self._safe_write(f'    Save error: {e}', self.style.ERROR)

    def _save_news(self, source, title, link, description, published_date, category):
        """Save as regular NewsItem with the detected category."""
        try:
            NewsItem.objects.get_or_create(
                link=link,
                defaults={
                    'source': source,
                    'title': title,
                    'description': description,
                    'published_date': published_date,
                    'category': category,
                }
            )
        except Exception as e:
            self._safe_write(f'    Save error: {e}', self.style.ERROR)

    # ═══════════════════════════════════════════════════════
    #  UTILITY METHODS
    # ═══════════════════════════════════════════════════════

    def _is_duplicate(self, title, source):
        """Fuzzy deduplication using Levenshtein distance (thefuzz library)."""
        from thefuzz import fuzz
        
        recent_items = NewsItem.objects.filter(
            source=source
        ).order_by('-published_date')[:50]
        
        for existing in recent_items:
            if fuzz.token_set_ratio(title.lower(), existing.title.lower()) > 90:
                return True
        return False

    def _parse_date(self, entry):
        """Parse published date from RSS entry, fallback to now()."""
        for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    dt = datetime(*time_struct[:6])
                    return timezone.make_aware(dt, timezone.get_current_timezone())
                except Exception:
                    continue
        return timezone.now()

    def _extract_position(self, title, description):
        """
        Extract target position from content.
        Tier 1: Gemini AI (accurate, understands context).
        Tier 2: Regex fallback (fast, free).
        """
        from django.conf import settings
        
        clean_title = strip_tags(title)
        clean_desc = strip_tags(description)
        combined_text = (clean_title + ' ' + clean_desc).strip()
        
        # ── Gemini AI Position Extraction ──
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""You are a football/soccer data extractor. Read the following text from a club's post.
Determine the specific player position(s) they are recruiting for.
If this is a staff, managerial, medical, volunteer, or coaching role (NOT a playing role), return "is_staff_role": true.
If it is a player role, return standard position names (e.g., "Goalkeeper", "Striker", "Center Back").
Return ONLY a JSON object, no markdown:
{{"is_staff_role": <boolean>, "positions": ["<Position 1>", "<Position 2>"]}}

Text: {combined_text[:500]}"""
                
                response = model.generate_content(prompt)
                raw = response.text.strip().removeprefix('```json').removesuffix('```').strip()
                result = json.loads(raw)
                
                if result.get("is_staff_role", False):
                    return ''
                
                positions = [p.title() for p in result.get("positions", []) if p]
                if positions:
                    self._safe_write(f"    [GEMINI] Positions: {', '.join(positions)}", self.style.SUCCESS)
                    return ', '.join(positions)
                
            except Exception as e:
                self._safe_write(f"    [GEMINI] Position extraction failed: {e}", self.style.ERROR)
        
        # ── Regex Fallback ──
        combined_lower = combined_text.lower()
        
        # Check if staff role
        staff_patterns = [
            'manager', 'coach', 'assistant manager', 'head coach',
            'physiotherapist', 'physio', 'kit man', 'groundsman',
            'volunteer', 'administrator', 'secretary', 'treasurer',
            'committee', 'director', 'chairman', 'staff',
        ]
        for kw in staff_patterns:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_lower):
                return ''
        
        position_patterns = {
            'Goalkeeper': [r'\bgoalkeeper\b', r'\bkeeper\b', r'\bgk\b', r'\bgoalie\b'],
            'Defender': [r'\bdefender\b', r'\bcentre back\b', r'\bcenter back\b', r'\bcb\b', r'\bfull back\b'],
            'Left Back': [r'\bleft back\b', r'\bleft-back\b', r'\blb\b'],
            'Right Back': [r'\bright back\b', r'\bright-back\b', r'\brb\b'],
            'Midfielder': [r'\bmidfielder\b', r'\bmidfield\b', r'\bcm\b', r'\bcentral midfielder\b'],
            'Defensive Midfielder': [r'\bdefensive midfielder\b', r'\bcdm\b', r'\bholding midfielder\b'],
            'Attacking Midfielder': [r'\battacking midfielder\b', r'\bcam\b', r'\bplaymaker\b'],
            'Winger': [r'\bwinger\b', r'\bwide player\b', r'\blw\b', r'\brw\b'],
            'Striker': [r'\bstriker\b', r'\bforward\b', r'\bcentre forward\b', r'\bcenter forward\b'],
        }
        
        found = []
        for pos_name, patterns in position_patterns.items():
            for p in patterns:
                if re.search(p, combined_lower):
                    if pos_name not in found:
                        found.append(pos_name)
                    break
        
        return ', '.join(found)
