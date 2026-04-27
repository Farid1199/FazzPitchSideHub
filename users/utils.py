"""
Hybrid Recommendation Engine for FazzPitchSideHub.

Implements a 6-layer scoring system combining:
1. Rule-based filtering (open trials only)
2. Content-based scoring (position, level, location)
3. NLP text matching (TF-IDF + cosine similarity)
4. Collaborative filtering (similar players' interests)
5. Behavioral boosting (view history)
6. Freshness ranking (newer trials scored higher)

Industry parallels:
- LinkedIn Jobs: content-based + collaborative + behavioral
- Indeed: content-based + freshness
- Spotify: TF-IDF + collaborative filtering
"""
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import (
    Opportunity, PlayerProfile, ClubProfile, ClubSource,
    TrialView, TrialApplication
)


# ============================================================
# POSITION MAPPING
# Maps structured PlayerProfile position codes to descriptive
# football terms used in trial descriptions and RSS feeds.
# ============================================================
POSITION_TEXT_MAP = {
    'GK': 'goalkeeper keeper goalie shot stopper',
    'LB': 'left back fullback full back defender left sided defender',
    'CB': 'centre back center back central defender defender stopper',
    'RB': 'right back fullback full back defender right sided defender',
    'LWB': 'left wing back wingback left sided defender',
    'RWB': 'right wing back wingback right sided defender',
    'CDM': 'defensive midfielder holding midfielder midfield anchor shield',
    'CM': 'central midfielder midfield midfielder box to box engine',
    'CAM': 'attacking midfielder playmaker number ten creative',
    'LM': 'left midfielder left midfield wide midfielder winger left sided',
    'RM': 'right midfielder right midfield wide midfielder winger right sided',
    'LW': 'left winger wide forward left wing attacker',
    'RW': 'right winger wide forward right wing attacker',
    'ST': 'striker forward frontman target man centre forward attacker number nine',
    'CF': 'centre forward striker forward attacker clinical finisher number nine',
}

LEVEL_TEXT_MAP = {
    'STEP_1': 'national league step 1 professional semi professional',
    'STEP_2': 'national league north south step 2 semi professional',
    'STEP_3': 'isthmian northern southern premier step 3',
    'STEP_4': 'isthmian northern southern division one step 4',
    'STEP_5': 'regional leagues step 5',
    'STEP_6': 'county leagues step 6',
    'STEP_7': 'local leagues step 7',
    'SUNDAY': 'sunday league casual recreational grassroots',
    'OTHER': 'other level',
}


def _build_player_text(player_profile):
    """
    Build a text representation of a player's profile for NLP matching.
    Combines position keywords, level keywords, and location into a
    single text string that TF-IDF can vectorize.
    """
    parts = []

    # Add position keywords
    position_text = POSITION_TEXT_MAP.get(player_profile.position, '')
    if position_text:
        # Repeat position text to give it more weight in TF-IDF
        parts.append(position_text)
        parts.append(position_text)

    # Add level keywords
    level_text = LEVEL_TEXT_MAP.get(player_profile.playing_level, '')
    if level_text:
        parts.append(level_text)

    # Add location
    if player_profile.location_postcode:
        parts.append(player_profile.location_postcode)

    return ' '.join(parts)


def _build_trial_text(opportunity):
    """
    Build a text representation of a trial opportunity for NLP matching.
    Combines title, description, target position, and club info.
    """
    parts = []

    # Title and description (the main content)
    if opportunity.title:
        parts.append(opportunity.title)
    if opportunity.description:
        parts.append(opportunity.description)

    # Target position (if specified)
    if opportunity.target_position:
        parts.append(opportunity.target_position)

    # Club information (league level context)
    if opportunity.source:
        # RSS-sourced: use ClubSource data
        parts.append(opportunity.source.name)
        level_text = LEVEL_TEXT_MAP.get(opportunity.source.league_level, '')
        if level_text:
            parts.append(level_text)
        if opportunity.source.region:
            parts.append(opportunity.source.region)
    elif opportunity.club:
        # Club-posted: use ClubProfile data
        parts.append(opportunity.club.club_name)
        level_text = LEVEL_TEXT_MAP.get(opportunity.club.league_level, '')
        if level_text:
            parts.append(level_text)
        if opportunity.club.location_postcode:
            parts.append(opportunity.club.location_postcode)

    return ' '.join(parts)


def _get_nlp_scores(player_profile, opportunities):
    """
    Calculate NLP similarity scores between a player profile and trial opportunities
    using TF-IDF vectorization and cosine similarity.

    How it works:
    1. Build text representations for the player and each trial
    2. Use TF-IDF to convert text into numerical vectors
    3. Calculate cosine similarity between player vector and each trial vector
    4. Return similarity scores (0.0 to 1.0) for each opportunity

    This catches semantic matches that keyword matching misses, e.g.:
    - "bolster the backline" → matches a defender
    - "clinical finisher up top" → matches a striker
    """
    if not opportunities:
        return {}

    player_text = _build_player_text(player_profile)
    trial_texts = [_build_trial_text(opp) for opp in opportunities]

    # Combine player text with all trial texts for TF-IDF fitting
    all_texts = [player_text] + trial_texts

    try:
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)  # Use unigrams and bigrams for better matching
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Calculate cosine similarity between player (index 0) and all trials
        player_vector = tfidf_matrix[0:1]
        trial_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(player_vector, trial_vectors)[0]

        # Map opportunity IDs to similarity scores
        return {opp.pk: float(sim) for opp, sim in zip(opportunities, similarities)}

    except Exception:
        # If NLP fails for any reason, return empty scores (graceful degradation)
        return {}


def _get_location_match(player_postcode, opportunity):
    """
    Check if a trial is in a similar location to the player.
    Uses UK postcode area matching (first letters before the number).

    For example:
    - Player: "B23 6TH" → area "B"
    - Club: "B44 8NR" → area "B" → MATCH
    - Club: "CV1 2WT" → area "CV" → NO MATCH

    For RSS-sourced trials, falls back to region matching.
    """
    if not player_postcode:
        return False

    # Extract postcode area (letters before first digit)
    player_area = ''
    for char in player_postcode.strip():
        if char.isalpha():
            player_area += char.upper()
        else:
            break

    if not player_area:
        return False

    # Check club-posted opportunities
    if opportunity.club and opportunity.club.location_postcode:
        club_area = ''
        for char in opportunity.club.location_postcode.strip():
            if char.isalpha():
                club_area += char.upper()
            else:
                break
        return player_area == club_area

    # Check RSS-sourced opportunities (use region)
    if opportunity.source and opportunity.source.region:
        # Simple region check — if player postcode area maps to the region
        # Birmingham postcodes start with "B", which maps to Birmingham region
        region_lower = opportunity.source.region.lower()
        postcode_region_map = {
            'B': 'birmingham',
            'CV': 'coventry',
            'WS': 'walsall',
            'WV': 'wolverhampton',
            'DY': 'dudley',
            'ST': 'stoke',
            'DE': 'derby',
            'LE': 'leicester',
            'NG': 'nottingham',
        }
        mapped_region = postcode_region_map.get(player_area, '').lower()
        if mapped_region and mapped_region in region_lower:
            return True
        # Also check West Midlands as a broader match
        if player_area in ['B', 'CV', 'WS', 'WV', 'DY'] and 'west midlands' in region_lower:
            return True

    return False


def get_recommendations(player_profile):
    """
    Hybrid Recommendation Engine — 6-layer scoring system.

    Layer 1: Rule-based filtering (only open trials)
    Layer 2: Content-based scoring (position +10, level +5, location +3)
    Layer 3: NLP text matching (TF-IDF cosine similarity, up to +8)
    Layer 4: Collaborative filtering (similar players' interests, +6)
    Layer 5: Behavioral boosting (viewed +2, already applied -100)
    Layer 6: Freshness ranking (newer trials get up to +5)

    Args:
        player_profile: PlayerProfile instance

    Returns:
        List of dicts with 'opportunity', 'score', and 'match_quality' keys.
        Top 5 results, sorted by score descending.
    """

    # ============================================================
    # LAYER 1: RULE-BASED FILTERING
    # Only consider open trials. Same as Indeed/LinkedIn filtering
    # out expired job listings before any scoring.
    # ============================================================
    opportunities = list(
        Opportunity.objects.select_related('club', 'source').filter(
            is_open=True,
            category='trial',
            target_position__isnull=False,
        ).exclude(target_position__exact='')
    )

    if not opportunities:
        return []

    # ============================================================
    # LAYER 3: NLP TEXT MATCHING (compute first, used in scoring)
    # TF-IDF + cosine similarity between player profile text and
    # trial descriptions. Catches semantic matches keywords miss.
    # ============================================================
    nlp_scores = _get_nlp_scores(player_profile, opportunities)

    # ============================================================
    # LAYER 4: COLLABORATIVE FILTERING (pre-compute)
    # Find players with same position + level, see what they applied to.
    # "Players like you were interested in these trials."
    # ============================================================
    similar_players = PlayerProfile.objects.filter(
        position=player_profile.position,
        playing_level=player_profile.playing_level
    ).exclude(pk=player_profile.pk)

    # Trials that similar players expressed interest in
    similar_applied_ids = set(
        TrialApplication.objects.filter(
            player__in=similar_players
        ).values_list('opportunity_id', flat=True)
    )

    # ============================================================
    # LAYER 5: BEHAVIORAL (pre-compute)
    # What trials has THIS player viewed or applied to?
    # ============================================================
    player_viewed_ids = set(
        TrialView.objects.filter(
            player=player_profile
        ).values_list('opportunity_id', flat=True)
    )

    player_applied_ids = set(
        TrialApplication.objects.filter(
            player=player_profile
        ).values_list('opportunity_id', flat=True)
    )

    # ============================================================
    # SCORING: Apply all layers to each opportunity
    # ============================================================
    scored_opportunities = []

    for opportunity in opportunities:
        score = 0
        match_reasons = []

        # ------ LAYER 2: CONTENT-BASED SCORING ------

        # Position match (+10) — the strongest signal
        if opportunity.target_position:
            player_position_code = player_profile.position
            player_position_display = player_profile.get_position_display().lower()
            target_lower = opportunity.target_position.lower()

            if (player_position_code in opportunity.target_position or
                    player_position_display in target_lower):
                score += 10
                match_reasons.append('position')

        # League level match (+5)
        trial_level = None
        if opportunity.source:
            trial_level = opportunity.source.league_level
        elif opportunity.club:
            trial_level = opportunity.club.league_level

        if trial_level and trial_level == player_profile.playing_level:
            score += 5
            match_reasons.append('level')

        # Location match (+3)
        if _get_location_match(player_profile.location_postcode, opportunity):
            score += 3
            match_reasons.append('location')

        # ------ LAYER 3: NLP SCORE ------
        # Scale cosine similarity (0-1) to 0-8 points
        nlp_score = nlp_scores.get(opportunity.pk, 0.0)
        nlp_points = round(nlp_score * 8, 2)
        if nlp_points > 0.5:  # Only add if meaningful similarity
            score += nlp_points
            if nlp_points >= 3:
                match_reasons.append('nlp')

        # ------ LAYER 4: COLLABORATIVE FILTERING ------
        if opportunity.pk in similar_applied_ids:
            score += 6
            match_reasons.append('collaborative')

        # ------ LAYER 5: BEHAVIORAL BOOSTING ------
        if opportunity.pk in player_applied_ids:
            # Already applied — suppress this trial
            score -= 100
        elif opportunity.pk in player_viewed_ids:
            # Viewed but not applied — signals interest
            score += 2
            match_reasons.append('viewed')

        # ------ LAYER 6: FRESHNESS RANKING ------
        if opportunity.published_date:
            days_old = (timezone.now() - opportunity.published_date).days
            freshness_boost = max(0, 5 - days_old)
            score += freshness_boost
            if freshness_boost >= 3:
                match_reasons.append('fresh')

        # Determine match quality label for the UI
        if score >= 20:
            match_quality = 'excellent'
        elif score >= 13:
            match_quality = 'strong'
        elif score >= 8:
            match_quality = 'good'
        elif score > 0:
            match_quality = 'fair'
        else:
            match_quality = 'none'

        # Prevent weak suggestions caused only by freshness. A trial must have
        # at least one real matching signal to be shown as a recommendation.
        core_match_signals = {'position', 'level', 'location', 'nlp', 'collaborative', 'viewed'}
        has_core_match = bool(core_match_signals.intersection(match_reasons))

        scored_opportunities.append({
            'opportunity': opportunity,
            'score': score,
            'match_quality': match_quality,
            'match_reasons': match_reasons,
            'has_core_match': has_core_match,
        })

    # Filter out score <= 0 (unmatched or suppressed)
    matched = [
        item for item in scored_opportunities
        if item['score'] > 0 and item['has_core_match']
    ]

    # Sort by score (highest first), then by freshness
    matched.sort(
        key=lambda x: (x['score'], x['opportunity'].published_date),
        reverse=True
    )

    # Return top 5 recommendations
    return matched[:5]
