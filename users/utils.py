"""
Utility functions for the users app.
Contains recommendation engine and other helper functions.
"""
from .models import Opportunity, PlayerProfile


def get_recommendations(player_profile):
    """
    Intelligent matching algorithm for player recommendations.
    
    Scores each opportunity based on:
    - +10 points if target_position matches player's position
    - +5 points if league_level matches player's playing_level
    
    Args:
        player_profile: PlayerProfile instance
        
    Returns:
        List of top 3 Opportunity objects with highest scores
    """
    # Get all open opportunities
    opportunities = Opportunity.objects.select_related('club').filter(is_open=True)
    
    # Score each opportunity
    scored_opportunities = []
    
    for opportunity in opportunities:
        score = 0
        
        # +10 points for matching position
        if opportunity.target_position:
            # Check if player's position is mentioned in target_position
            # target_position might contain multiple positions like "Striker, Forward"
            if player_profile.position in opportunity.target_position or \
               player_profile.get_position_display().lower() in opportunity.target_position.lower():
                score += 10
        
        # +5 points for matching league level
        if hasattr(opportunity.club, 'league_level'):
            if opportunity.club.league_level == player_profile.playing_level:
                score += 5
        
        # Store opportunity with its score
        scored_opportunities.append({
            'opportunity': opportunity,
            'score': score
        })
    
    # Sort by score (highest first), then by published date (most recent first)
    scored_opportunities.sort(key=lambda x: (x['score'], x['opportunity'].published_date), reverse=True)
    
    # Return top 3 opportunities
    top_matches = [item['opportunity'] for item in scored_opportunities[:3]]
    
    return top_matches
