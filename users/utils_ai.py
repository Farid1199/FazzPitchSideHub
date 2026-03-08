"""
AI Player Bio Generator using Google Gemini.
"""
import google.generativeai as genai
from django.conf import settings


def generate_player_bio(player_profile):
    """
    Generate a professional player bio using Google Gemini.
    Returns a string of 2-3 sentences.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    Write a professional 2-3 sentence football player profile bio
    for a non-league football player. Make it sound confident and
    professional, suitable for a scouting platform. Use only the
    information provided. Do not invent stats or achievements.

    Player details:
    - Position: {player_profile.get_position_display()}
    - Playing level: {player_profile.get_playing_level_display()}
    - Preferred foot: {player_profile.get_preferred_foot_display() if player_profile.preferred_foot else 'Not specified'}
    - Height: {player_profile.height}cm
    - Previous clubs: {player_profile.previous_clubs or 'Not specified'}
    - Current team: {player_profile.current_team or 'Free Agent'}

    Write only the bio text. No labels, no headings, no
    introductory phrases like "Here is a bio:". Just the
    professional bio paragraph.
    """

    response = model.generate_content(prompt)
    return response.text.strip()
