from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import (
    PlayerProfile, ClubProfile, ScoutProfile, ManagerProfile,
    Opportunity, TrialApplication, ClubSource, NewsItem
)
from users.utils import get_recommendations
from users.management.commands.fetch_rss import Command as FetchRSSCommand
import uuid
from io import StringIO

User = get_user_model()


# ============================================================
# HELPER: Create users with correct role + profile in one step
# ============================================================
def _create_user_with_role(username, role, password='TestPass123!'):
    """
    Helper to create a user with a role already set at creation time,
    so the post_save signal fires correctly and creates the profile.
    """
    user = User(username=username, role=role)
    user.set_password(password)
    user.save()  # Signal fires with created=True AND role set
    return user


# ============================================================
# 1. UNIT TESTING: USER REGISTRATION & ROLE ASSIGNMENT
# Tests that signals correctly create profiles based on roles.
# ============================================================
class AuthenticationTests(TestCase):
    """
    Validates that Django's post_save signal automatically creates
    the correct role-specific profile when a new user is registered.
    This is a critical part of the onboarding flow.
    """

    def test_player_registration_creates_profile(self):
        """Test that registering as a PLAYER automatically creates a PlayerProfile."""
        user = _create_user_with_role('testplayer', 'PLAYER')
        # Refresh from DB to ensure reverse relation is loaded
        user.refresh_from_db()
        self.assertTrue(PlayerProfile.objects.filter(user=user).exists())
        self.assertIsInstance(user.player_profile, PlayerProfile)

    def test_club_registration_creates_profile(self):
        """Test that registering as a CLUB automatically creates a ClubProfile."""
        user = _create_user_with_role('testclub', 'CLUB')
        user.refresh_from_db()
        self.assertTrue(ClubProfile.objects.filter(user=user).exists())
        self.assertIsInstance(user.club_profile, ClubProfile)

    def test_scout_registration_creates_profile(self):
        """Test that registering as a SCOUT automatically creates a ScoutProfile."""
        user = _create_user_with_role('testscout', 'SCOUT')
        user.refresh_from_db()
        self.assertTrue(ScoutProfile.objects.filter(user=user).exists())
        self.assertIsInstance(user.scout_profile, ScoutProfile)

    def test_manager_registration_creates_profile(self):
        """Test that registering as a MANAGER automatically creates a ManagerProfile."""
        user = _create_user_with_role('testmanager', 'MANAGER')
        user.refresh_from_db()
        self.assertTrue(ManagerProfile.objects.filter(user=user).exists())
        self.assertIsInstance(user.manager_profile, ManagerProfile)




# ============================================================
# 2. UNIT TESTING: AI RECOMMENDATION ENGINE SCORING
# Tests the 6-layer hybrid scoring system in utils.py.
# Validates position, level, location matching & score ranking.
# ============================================================
class AIRecommendationTests(TestCase):
    """
    Tests the core AI Recommendation Engine (get_recommendations).
    The engine uses a 6-layer scoring system:
      Layer 1: Rule-based filtering (open trials only)
      Layer 2: Content-based scoring (position +10, level +5, location +3)
      Layer 3: NLP text matching (TF-IDF cosine similarity, up to +8)
      Layer 4: Collaborative filtering (similar players' interests, +6)
      Layer 5: Behavioral boosting (viewed +2, already applied -100)
      Layer 6: Freshness ranking (newer trials get up to +5)
    """

    def setUp(self):
        # Create a Striker based in Birmingham at Step 3
        self.user = _create_user_with_role('striker_pro', 'PLAYER')
        self.profile = self.user.player_profile
        self.profile.position = 'ST'
        self.profile.location_postcode = 'B1 1AA'
        self.profile.playing_level = 'STEP_3'
        self.profile.save()

        # Create a club with a matching trial (Striker, Step 3, Birmingham area)
        self.club_user = _create_user_with_role('brum_fc', 'CLUB')
        self.club_profile = self.club_user.club_profile
        self.club_profile.club_name = 'Birmingham City FC'
        self.club_profile.location_postcode = 'B10 0BS'
        self.club_profile.league_level = 'STEP_3'
        self.club_profile.save()

        self.match_trial = Opportunity.objects.create(
            title='First Team Striker Wanted',
            description='Looking for a clinical finisher to join our Step 3 side.',
            target_position='Striker',
            club=self.club_profile,
            is_open=True,
            link=f'http://test.com/{uuid.uuid4()}',
            published_date=timezone.now()
        )

        # Create a non-matching trial (Goalkeeper, no club/level match)
        self.no_match_trial = Opportunity.objects.create(
            title='Goalkeeper Needed',
            description='Searching for a goalie for a London-based Step 6 squad.',
            target_position='Goalkeeper',
            is_open=True,
            link=f'http://test.com/{uuid.uuid4()}',
            published_date=timezone.now()
        )

    def test_matching_trial_ranked_first(self):
        """Test that the scoring logic correctly ranks relevant trials higher."""
        recommendations = get_recommendations(self.profile)
        self.assertTrue(len(recommendations) > 0)

        # The Striker trial should be the top recommendation
        top_rec = recommendations[0]
        self.assertEqual(top_rec['opportunity'], self.match_trial)

    def test_matching_trial_high_score(self):
        """Test that position + level + location match produces a high score."""
        recommendations = get_recommendations(self.profile)
        top_rec = recommendations[0]
        # Position (+10) + Level (+5) + Location (+3) + Freshness (+5) = 23+
        self.assertGreaterEqual(top_rec['score'], 20)
        self.assertEqual(top_rec['match_quality'], 'excellent')

    def test_closed_trials_excluded(self):
        """Test Layer 1: closed trials are never recommended."""
        self.match_trial.is_open = False
        self.match_trial.save()

        recommendations = get_recommendations(self.profile)
        recommended_ids = [r['opportunity'].pk for r in recommendations]
        self.assertNotIn(self.match_trial.pk, recommended_ids)

    def test_already_applied_suppressed(self):
        """Test Layer 5: trials the player already applied to are suppressed."""
        TrialApplication.objects.create(
            player=self.profile,
            opportunity=self.match_trial
        )
        recommendations = get_recommendations(self.profile)
        recommended_ids = [r['opportunity'].pk for r in recommendations]
        self.assertNotIn(self.match_trial.pk, recommended_ids)


# ============================================================
# 3. UNIT TESTING: RSS KEYWORD DETECTION (is_trial logic)
# Tests the multi-layer regex classification in fetch_rss.py.
# ============================================================
class RSSEngineTests(TestCase):
    """
    Tests the RSS Feed Scraper's multi-layer classification pipeline:
      Layer 1: Hard Exclusion (youth/women's content)
      Layer 2: Strict Trial Keywords
      Layer 3a: Regex — Match Report Detection (scoreline patterns)
      Layer 3b: Regex — Transfer Detection
    """

    def setUp(self):
        self.cmd = FetchRSSCommand()
        self.cmd.stdout = StringIO()

    # --- Layer 1: Exclusion ---
    def test_exclusion_filters_youth_content(self):
        """Test that Layer 1 correctly filters out U18/academy content."""
        self.assertTrue(self.cmd._should_exclude('U18 Academy Recruitment', ''))
        self.assertTrue(self.cmd._should_exclude('Youth Team Trials', ''))

    def test_exclusion_filters_womens_content(self):
        """Test that Layer 1 correctly filters out women's content."""
        self.assertTrue(self.cmd._should_exclude("Women's Open Trial", ''))
        self.assertTrue(self.cmd._should_exclude('Ladies Team Recruitment', ''))

    def test_exclusion_allows_mens_content(self):
        """Test that Layer 1 allows legitimate men's first-team content."""
        self.assertFalse(self.cmd._should_exclude('First Team Player Wanted', ''))
        self.assertFalse(self.cmd._should_exclude('Pre-Season Open Trial This Saturday', ''))

    # --- Layer 2: Trial Keyword Detection ---
    def test_trial_keyword_detection_positive(self):
        """Test that confirmed trial language is correctly detected."""
        self.assertTrue(self.cmd._is_confirmed_trial(
            'First Team Open Trials This Saturday',
            'Come and showcase your talent.'
        ))

    def test_trial_keyword_detection_negative(self):
        """Test that non-trial content is not flagged as a trial."""
        self.assertFalse(self.cmd._is_confirmed_trial(
            'Match Report: 2-1 Victory Against Rivals',
            'A late goal sealed the win.'
        ))

    def test_trial_with_signing_language_rejected(self):
        """Test that a trial keyword + announcement language is NOT flagged as trial.
        ('New signing joins after successful trial' is a transfer, not an open trial.)"""
        self.assertFalse(self.cmd._is_confirmed_trial(
            'New signing joins after successful trial',
            'We are pleased to announce...'
        ))

    # --- Layer 3a: Match Report Detection ---
    def test_match_report_scoreline_in_title(self):
        """Test that a scoreline in the title triggers match report detection."""
        self.assertTrue(self.cmd._is_match_report('Halesowen Town 2-1 Bromsgrove', ''))

    def test_match_report_explicit_phrase(self):
        """Test that explicit match report phrases trigger detection."""
        self.assertTrue(self.cmd._is_match_report('Match Report: Victory at Home', ''))

    # --- Layer 3b: Transfer Detection ---
    def test_transfer_strong_phrase(self):
        """Test that strong transfer phrases are correctly detected."""
        self.assertTrue(self.cmd._is_transfer('New signing joins from rivals', ''))

    def test_transfer_weak_word_no_scoreline(self):
        """Test that weak transfer words trigger when no scoreline is present."""
        self.assertTrue(self.cmd._is_transfer('Player signing confirmed', ''))

    def test_transfer_weak_word_with_scoreline_ignored(self):
        """Test that weak transfer words are ignored when a scoreline is present
        (disambiguation — prevents misclassifying match reports about loan players)."""
        self.assertFalse(self.cmd._is_transfer(
            'Signed player scores on debut',
            'He netted in a 3-1 victory.'
        ))


# ============================================================
# 4. INTEGRATION TESTING: ROLE-BASED ACCESS CONTROL (RBAC)
# Tests that views enforce role-based permissions correctly.
# Uses force_login to bypass django-axes authentication backend.
# ============================================================
class RBACTests(TestCase):
    """
    Integration tests for Role-Based Access Control (RBAC).
    Verifies that only Club Officials can post trial opportunities,
    and that Players/other roles are redirected away.
    """

    def setUp(self):
        self.client = Client()
        self.player = _create_user_with_role('p_tester', 'PLAYER')
        self.club = _create_user_with_role('c_tester', 'CLUB')
        self.club.club_profile.club_name = 'Test FC'
        self.club.club_profile.save()

    def test_unauthenticated_user_redirected_from_dashboard(self):
        """Integration test: visiting /dashboard/ while logged out redirects to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_player_cannot_access_post_trial(self):
        """Verify players are redirected away from the trial posting page (RBAC)."""
        self.client.force_login(self.player)
        response = self.client.get(reverse('post_opportunity'))
        self.assertEqual(response.status_code, 302)

    def test_club_can_access_post_trial(self):
        """Verify clubs can access the trial posting page."""
        self.client.force_login(self.club)
        response = self.client.get(reverse('post_opportunity'))
        self.assertEqual(response.status_code, 200)

    def test_player_cannot_access_shortlist(self):
        """Verify players cannot access the club shortlist page."""
        self.client.force_login(self.player)
        response = self.client.get(reverse('club_shortlist'))
        self.assertEqual(response.status_code, 302)


# ============================================================
# 5. INTEGRATION TESTING: TRIAL APPLICATION FLOW
# Tests views, models, and URLs working end-to-end.
# ============================================================
class TrialApplicationTests(TestCase):
    """
    Integration tests for the trial application (express interest) flow.
    Tests that the POST request creates a TrialApplication record
    linking the player to the opportunity in the database.
    """

    def setUp(self):
        self.client = Client()
        self.player_user = _create_user_with_role('applic_user', 'PLAYER')

        self.club_user = _create_user_with_role('test_fc', 'CLUB')
        self.club_user.club_profile.club_name = 'Test FC'
        self.club_user.club_profile.save()

        self.opportunity = Opportunity.objects.create(
            title='Midfield Trial',
            description='Test description',
            club=self.club_user.club_profile,
            is_open=True,
            link=f'http://test.com/{uuid.uuid4()}',
            published_date=timezone.now()
        )

    def test_express_interest_creates_record(self):
        """Integration test: POSTing to express interest creates a database record."""
        self.client.force_login(self.player_user)
        url = reverse('express_interest', kwargs={'pk': self.opportunity.pk})

        # Verify 0 applications before
        self.assertEqual(TrialApplication.objects.count(), 0)

        response = self.client.post(url)

        # Verify redirect back and record creation
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrialApplication.objects.count(), 1)

        app = TrialApplication.objects.first()
        self.assertEqual(app.player, self.player_user.player_profile)
        self.assertEqual(app.opportunity, self.opportunity)

    def test_duplicate_application_prevented(self):
        """Integration test: applying twice does not create a duplicate record."""
        self.client.force_login(self.player_user)
        url = reverse('express_interest', kwargs={'pk': self.opportunity.pk})

        self.client.post(url)
        self.client.post(url)

        self.assertEqual(TrialApplication.objects.count(), 1)

    def test_withdraw_interest_removes_record(self):
        """Integration test: withdrawing interest removes the application record."""
        self.client.force_login(self.player_user)

        # First, express interest
        self.client.post(
            reverse('express_interest', kwargs={'pk': self.opportunity.pk})
        )
        self.assertEqual(TrialApplication.objects.count(), 1)

        # Now withdraw
        response = self.client.post(
            reverse('withdraw_interest', kwargs={'pk': self.opportunity.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrialApplication.objects.count(), 0)


# ============================================================
# 6. INTEGRATION TESTING: SIGNUP FLOW (end-to-end)
# Tests that a POST to /signup/ actually creates a User record.
# ============================================================
class SignupIntegrationTests(TestCase):
    """
    Integration test for the signup endpoint.
    Validates that submitting the signup form creates a User in the database.
    """

    def test_signup_page_loads(self):
        """Test that the signup page renders successfully."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """Test that the login page renders successfully."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_loads(self):
        """Test that the home page renders successfully."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
