"""
Script to create test players and managers for all positions.
Run this script with: python populate_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from users.models import PlayerProfile, ManagerProfile, ScoutProfile

User = get_user_model()

# Test users data with all positions
TEST_USERS = [
    # Goalkeepers
    {
        'username': 'gk_james',
        'email': 'james.keeper@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'GK',
            'current_team': 'Local FC',
            'available_for_club': True,
            'location_postcode': 'E14 5AB',
            'playing_level': 'STEP_5',
            'height': 1.88,
            'preferred_foot': 'RIGHT',
            'youtube_highlight_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'previous_clubs': 'Youth FC, Academy FC',
        }
    },
    {
        'username': 'gk_david',
        'email': 'david.goalkeeper@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'GK',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'SW1A 1AA',
            'playing_level': 'STEP_6',
            'height': 1.91,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Rangers FC, City Academy',
        }
    },
    
    # Defenders - Left Back
    {
        'username': 'lb_marcus',
        'email': 'marcus.leftback@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'LB',
            'current_team': 'United FC',
            'available_for_club': True,
            'location_postcode': 'M1 1AD',
            'playing_level': 'STEP_4',
            'height': 1.78,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Youth United, Academy FC',
        }
    },
    {
        'username': 'lb_andy',
        'email': 'andy.defender@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'LB',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'B2 4QA',
            'playing_level': 'STEP_5',
            'height': 1.75,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Birmingham Youth, Villa Academy',
        }
    },
    
    # Defenders - Centre Back
    {
        'username': 'cb_john',
        'email': 'john.centreback@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CB',
            'current_team': 'City FC',
            'available_for_club': False,
            'location_postcode': 'L1 8JQ',
            'playing_level': 'STEP_3',
            'height': 1.85,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Liverpool Youth, Everton Academy',
        }
    },
    {
        'username': 'cb_michael',
        'email': 'michael.defender@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CB',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'LS1 1BA',
            'playing_level': 'STEP_4',
            'height': 1.90,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Leeds Youth, Bradford FC',
        }
    },
    {
        'username': 'cb_terry',
        'email': 'terry.centreback@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CB',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'NE1 1EE',
            'playing_level': 'STEP_5',
            'height': 1.87,
            'preferred_foot': 'BOTH',
            'previous_clubs': 'Newcastle Youth, Sunderland Academy',
        }
    },
    
    # Defenders - Right Back
    {
        'username': 'rb_kyle',
        'email': 'kyle.rightback@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'RB',
            'current_team': 'Rangers FC',
            'available_for_club': True,
            'location_postcode': 'G1 1AA',
            'playing_level': 'STEP_4',
            'height': 1.77,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Celtic Youth, Hamilton FC',
        }
    },
    {
        'username': 'rb_trent',
        'email': 'trent.fullback@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'RB',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'L8 1AE',
            'playing_level': 'STEP_5',
            'height': 1.75,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Liverpool Youth',
        }
    },
    
    # Midfielders - CDM
    {
        'username': 'cdm_declan',
        'email': 'declan.midfielder@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CDM',
            'current_team': 'Hammers FC',
            'available_for_club': True,
            'location_postcode': 'E20 2ST',
            'playing_level': 'STEP_3',
            'height': 1.85,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'West Ham Youth, Chelsea Academy',
        }
    },
    {
        'username': 'cdm_casemiro',
        'email': 'casemiro.dm@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CDM',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'M16 0RA',
            'playing_level': 'STEP_4',
            'height': 1.83,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Madrid Youth, Porto FC',
        }
    },
    
    # Midfielders - CM
    {
        'username': 'cm_kevin',
        'email': 'kevin.midfielder@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CM',
            'current_team': 'City FC',
            'available_for_club': False,
            'location_postcode': 'M11 3FF',
            'playing_level': 'STEP_2',
            'height': 1.81,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Genk FC, Wolfsburg FC',
        }
    },
    {
        'username': 'cm_luka',
        'email': 'luka.central@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CM',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'N17 0AP',
            'playing_level': 'STEP_4',
            'height': 1.72,
            'preferred_foot': 'BOTH',
            'previous_clubs': 'Dinamo Zagreb, Spurs Youth',
        }
    },
    {
        'username': 'cm_bruno',
        'email': 'bruno.playmaker@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CM',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'M16 0RA',
            'playing_level': 'STEP_5',
            'height': 1.79,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Sporting Lisbon, Sampdoria FC',
        }
    },
    
    # Midfielders - CAM
    {
        'username': 'cam_martin',
        'email': 'martin.attacking@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CAM',
            'current_team': 'Arsenal FC',
            'available_for_club': True,
            'location_postcode': 'N5 1BU',
            'playing_level': 'STEP_3',
            'height': 1.69,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Madrid Youth, Real Sociedad',
        }
    },
    {
        'username': 'cam_mason',
        'email': 'mason.creator@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CAM',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'SW6 1HS',
            'playing_level': 'STEP_4',
            'height': 1.75,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Chelsea Youth, Derby County',
        }
    },
    
    # Wingers - LW
    {
        'username': 'lw_raheem',
        'email': 'raheem.winger@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'LW',
            'current_team': 'Blues FC',
            'available_for_club': True,
            'location_postcode': 'SW6 1HS',
            'playing_level': 'STEP_3',
            'height': 1.70,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Liverpool Youth, Man City',
        }
    },
    {
        'username': 'lw_jack',
        'email': 'jack.leftwing@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'LW',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'B6 6HE',
            'playing_level': 'STEP_5',
            'height': 1.75,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Aston Villa Youth, Notts County',
        }
    },
    
    # Wingers - RW
    {
        'username': 'rw_mohamed',
        'email': 'mohamed.winger@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'RW',
            'current_team': 'Liverpool FC',
            'available_for_club': False,
            'location_postcode': 'L4 0TH',
            'playing_level': 'STEP_2',
            'height': 1.75,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Basel FC, Roma FC',
        }
    },
    {
        'username': 'rw_bukayo',
        'email': 'bukayo.rightwing@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'RW',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'N5 1BU',
            'playing_level': 'STEP_4',
            'height': 1.78,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Arsenal Youth',
        }
    },
    
    # Strikers - ST
    {
        'username': 'st_harry',
        'email': 'harry.striker@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'ST',
            'current_team': 'Bayern FC',
            'available_for_club': True,
            'location_postcode': 'N17 0AP',
            'playing_level': 'STEP_1',
            'height': 1.88,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Spurs Youth, Leicester City',
        }
    },
    {
        'username': 'st_erling',
        'email': 'erling.goalscorer@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'ST',
            'current_team': 'City FC',
            'available_for_club': False,
            'location_postcode': 'M11 3FF',
            'playing_level': 'STEP_1',
            'height': 1.94,
            'preferred_foot': 'LEFT',
            'previous_clubs': 'Salzburg FC, Dortmund FC',
        }
    },
    {
        'username': 'st_victor',
        'email': 'victor.forward@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'ST',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'N5 1BU',
            'playing_level': 'STEP_4',
            'height': 1.82,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Lille FC, Arsenal Youth',
        }
    },
    {
        'username': 'st_ivan',
        'email': 'ivan.striker@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'ST',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'NE1 4ST',
            'playing_level': 'STEP_6',
            'height': 1.80,
            'preferred_foot': 'BOTH',
            'previous_clubs': 'Brentford FC, Newcastle Youth',
        }
    },
    
    # Centre Forward
    {
        'username': 'cf_robert',
        'email': 'robert.centreforward@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CF',
            'current_team': 'Barcelona FC',
            'available_for_club': False,
            'location_postcode': 'M16 0RA',
            'playing_level': 'STEP_2',
            'height': 1.85,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Bayern Munich, Dortmund FC',
        }
    },
    {
        'username': 'cf_darwin',
        'email': 'darwin.forward@test.com',
        'password': 'TestPass123!',
        'role': 'PLAYER',
        'profile': {
            'position': 'CF',
            'current_team': '',
            'available_for_club': True,
            'location_postcode': 'L4 0TH',
            'playing_level': 'STEP_5',
            'height': 1.87,
            'preferred_foot': 'RIGHT',
            'previous_clubs': 'Benfica FC, Almeria FC',
        }
    },
]

# Test managers data
TEST_MANAGERS = [
    {
        'username': 'manager_alex',
        'email': 'alex.manager@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'United FC',
            'current_role': 'First Team Manager',
            'availability': 'EMPLOYED',
            'location_postcode': 'M16 0RA',
            'coaching_philosophy': 'I believe in attacking football with high pressing and quick transitions. Player development is at the heart of everything I do.',
            'preferred_formation': '4-3-3',
            'years_of_experience': 15,
            'career_history': 'United FC (2020-Present)\nCity Academy (2015-2020)\nYouth FC Coach (2010-2015)',
            'achievements': 'League Championship 2022\nCup Winner 2021\nPromotion 2019',
            'games_managed': 450,
            'win_rate': 62.5,
            'highest_qualification': 'UEFA_A',
            'additional_badges': 'FA Youth Award\nGoalkeeping Level 1',
            'qualification_verified': False,
        }
    },
    {
        'username': 'manager_jose',
        'email': 'jose.coach@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': '',
            'current_role': '',
            'availability': 'AVAILABLE',
            'location_postcode': 'SW6 1HS',
            'coaching_philosophy': 'Defensive stability first, counter-attacking football. I focus on team organization and tactical discipline.',
            'preferred_formation': '4-2-3-1',
            'years_of_experience': 25,
            'career_history': 'Roma FC (2018-2023)\nChelsea FC (2013-2018)\nReal Madrid (2010-2013)',
            'achievements': 'Champions League Winner 2015\nMultiple League Titles\n5x Manager of the Year',
            'games_managed': 1200,
            'win_rate': 68.3,
            'highest_qualification': 'UEFA_PRO',
            'additional_badges': 'Advanced Tactics Course\nSports Psychology Certificate',
            'qualification_verified': True,
        }
    },
    {
        'username': 'manager_pep',
        'email': 'pep.tactician@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'City FC',
            'current_role': 'Head Coach',
            'availability': 'EMPLOYED',
            'location_postcode': 'M11 3FF',
            'coaching_philosophy': 'Possession-based football with positional play. Building from the back and dominating the game through ball control.',
            'preferred_formation': '4-3-3',
            'years_of_experience': 18,
            'career_history': 'Manchester City (2016-Present)\nBayern Munich (2013-2016)\nBarcelona (2008-2012)',
            'achievements': 'Multiple League Titles\n2x Champions League Winner\nTreble Winner 2023',
            'games_managed': 900,
            'win_rate': 73.2,
            'highest_qualification': 'UEFA_PRO',
            'additional_badges': 'La Liga Coaching Badge\nAdvanced Analytics Course',
            'qualification_verified': True,
        }
    },
    {
        'username': 'manager_jurgen',
        'email': 'jurgen.pressing@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': '',
            'current_role': '',
            'availability': 'AVAILABLE',
            'location_postcode': 'L4 0TH',
            'coaching_philosophy': 'Heavy metal football! High intensity pressing, quick transitions, and passionate play. Team spirit is everything.',
            'preferred_formation': '4-3-3',
            'years_of_experience': 20,
            'career_history': 'Liverpool FC (2015-2024)\nBorussia Dortmund (2008-2015)\nMainz 05 (2001-2008)',
            'achievements': 'Champions League Winner 2019\nPremier League Champion 2020\nMultiple Cups',
            'games_managed': 1100,
            'win_rate': 65.8,
            'highest_qualification': 'UEFA_PRO',
            'additional_badges': 'German FA License\nSports Science Certification',
            'qualification_verified': True,
        }
    },
    {
        'username': 'manager_emma',
        'email': 'emma.tactician@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': 'Blues FC',
            'current_role': 'Manager',
            'availability': 'EMPLOYED',
            'location_postcode': 'SW6 1HS',
            'coaching_philosophy': 'Modern attacking football with tactical flexibility. Player welfare and development are my priorities.',
            'preferred_formation': '3-4-3',
            'years_of_experience': 8,
            'career_history': 'Chelsea FC (2021-Present)\nWomen\'s National Team (2018-2021)\nArsenal Academy (2015-2018)',
            'achievements': 'League Cup Winner 2023\nDomestic Double 2022\nCoach of the Year 2023',
            'games_managed': 280,
            'win_rate': 59.6,
            'highest_qualification': 'UEFA_A',
            'additional_badges': 'FA Level 4\nSafeguarding Certificate',
            'qualification_verified': False,
        }
    },
    {
        'username': 'manager_steve',
        'email': 'steve.developer@test.com',
        'password': 'TestPass123!',
        'role': 'MANAGER',
        'profile': {
            'club_name': '',
            'current_role': '',
            'availability': 'AVAILABLE',
            'location_postcode': 'NE1 4ST',
            'coaching_philosophy': 'Youth development specialist. I focus on building players from grassroots level with emphasis on technical skills and game intelligence.',
            'preferred_formation': '4-4-2',
            'years_of_experience': 12,
            'career_history': 'Newcastle Academy (2015-2023)\nSunderland Youth (2010-2015)',
            'achievements': 'Youth Cup Winner 2020\nAcademy League Champions 2022\nDeveloped 15+ professional players',
            'games_managed': 520,
            'win_rate': 54.2,
            'highest_qualification': 'UEFA_B',
            'additional_badges': 'FA Youth Modules 1-3\nFirst Aid Certified',
            'qualification_verified': False,
        }
    },
]

# Test scouts data
TEST_SCOUTS = [
    {
        'username': 'scout_david',
        'email': 'david.scout@test.com',
        'password': 'TestPass123!',
        'role': 'SCOUT',
        'profile': {
            'organization': 'Premier League Scouting Network',
            'region': 'London & South East',
        }
    },
    {
        'username': 'scout_maria',
        'email': 'maria.spotter@test.com',
        'password': 'TestPass123!',
        'role': 'SCOUT',
        'profile': {
            'organization': 'Independent Scout',
            'region': 'North West England',
        }
    },
    {
        'username': 'scout_john',
        'email': 'john.talent@test.com',
        'password': 'TestPass123!',
        'role': 'SCOUT',
        'profile': {
            'organization': 'Championship Talent Agency',
            'region': 'Midlands',
        }
    },
    {
        'username': 'scout_sarah',
        'email': 'sarah.observer@test.com',
        'password': 'TestPass123!',
        'role': 'SCOUT',
        'profile': {
            'organization': 'United FC',
            'region': 'National Coverage',
        }
    },
]

def create_test_users():
    """Create all test players, managers, and scouts"""
    
    created_users = []
    
    print("=" * 80)
    print("CREATING TEST USERS FOR FAZZPITCHSIDEHUB")
    print("=" * 80)
    print()
    
    # Create Players
    print("📋 CREATING PLAYERS")
    print("-" * 80)
    
    for user_data in TEST_USERS:
        try:
            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                print(f"⚠️  User '{user_data['username']}' already exists. Skipping...")
                continue
            
            # Use transaction to ensure both user and profile are created together
            with transaction.atomic():
                # Create user (this triggers signal that creates empty profile)
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role']
                )
                
                # Update the player profile created by signal with our data
                profile = user.player_profile
                for key, value in user_data['profile'].items():
                    setattr(profile, key, value)
                profile.save()
            
            created_users.append({
                'type': 'PLAYER',
                'username': user_data['username'],
                'email': user_data['email'],
                'password': user_data['password'],
                'position': user_data['profile']['position']
            })
            
            print(f"✅ Created player: {user_data['username']} ({user_data['profile']['position']})")
            
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {str(e)}")
    
    print()
    print("=" * 80)
    print("📋 CREATING MANAGERS")
    print("-" * 80)
    for manager_data in TEST_MANAGERS:
        try:
            # Check if user already exists
            if User.objects.filter(username=manager_data['username']).exists():
                print(f"⚠️  User '{manager_data['username']}' already exists. Skipping...")
                continue
            
            # Use transaction to ensure both user and profile are created together
            with transaction.atomic():
                # Create user (this triggers signal that creates empty profile)
                user = User.objects.create_user(
                    username=manager_data['username'],
                    email=manager_data['email'],
                    password=manager_data['password'],
                    role=manager_data['role']
                )
                
                # Update the manager profile created by signal with our data
                profile = user.manager_profile
                for key, value in manager_data['profile'].items():
                    setattr(profile, key, value)
                profile.save()
            
            created_users.append({
                'type': 'MANAGER',
                'username': manager_data['username'],
                'email': manager_data['email'],
                'password': manager_data['password'],
                'qualification': manager_data['profile']['highest_qualification']
            })
            
            print(f"✅ Created manager: {manager_data['username']} ({manager_data['profile']['highest_qualification']})")
            
        except Exception as e:
            print(f"❌ Error creating {manager_data['username']}: {str(e)}")
    
    print()
    print("=" * 80)
    print("📋 CREATING SCOUTS")
    print("-" * 80)
    for scout_data in TEST_SCOUTS:
        try:
            # Check if user already exists
            if User.objects.filter(username=scout_data['username']).exists():
                print(f"⚠️  User '{scout_data['username']}' already exists. Skipping...")
                continue
            
            # Use transaction to ensure both user and profile are created together
            with transaction.atomic():
                # Create user (this triggers signal that creates empty profile)
                user = User.objects.create_user(
                    username=scout_data['username'],
                    email=scout_data['email'],
                    password=scout_data['password'],
                    role=scout_data['role']
                )
                
                # Update the scout profile created by signal with our data
                profile = user.scout_profile
                for key, value in scout_data['profile'].items():
                    setattr(profile, key, value)
                profile.save()
            
            created_users.append({
                'type': 'SCOUT',
                'username': scout_data['username'],
                'email': scout_data['email'],
                'password': scout_data['password'],
                'organization': scout_data['profile']['organization']
            })
            
            print(f"✅ Created scout: {scout_data['username']} ({scout_data['profile']['organization']})")
            
        except Exception as e:
            print(f"❌ Error creating {scout_data['username']}: {str(e)}")
    
    print()
    print("=" * 80)
    print("✨ CREATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"Total users created: {len(created_users)}")
    print()
    
    return created_users


def print_login_credentials(created_users):
    """Print all login credentials in an organized format"""
    
    print()
    print("=" * 80)
    print("🔑 LOGIN CREDENTIALS FOR ALL TEST USERS")
    print("=" * 80)
    print()
    print("⚠️  SAVE THIS INFORMATION - ALL PASSWORDS ARE: TestPass123!")
    print()
    
    # Group by position
    players_by_position = {}
    managers = []
    scouts = []
    
    for user in created_users:
        if user['type'] == 'PLAYER':
            position = user['position']
            if position not in players_by_position:
                players_by_position[position] = []
            players_by_position[position].append(user)
        elif user['type'] == 'MANAGER':
            managers.append(user)
        elif user['type'] == 'SCOUT':
            scouts.append(user)
    
    # Print players by position
    print("👥 PLAYERS BY POSITION")
    print("-" * 80)
    
    position_names = {
        'GK': 'Goalkeepers',
        'LB': 'Left Backs',
        'CB': 'Centre Backs',
        'RB': 'Right Backs',
        'LWB': 'Left Wing Backs',
        'RWB': 'Right Wing Backs',
        'CDM': 'Defensive Midfielders',
        'CM': 'Central Midfielders',
        'CAM': 'Attacking Midfielders',
        'LM': 'Left Midfielders',
        'RM': 'Right Midfielders',
        'LW': 'Left Wingers',
        'RW': 'Right Wingers',
        'ST': 'Strikers',
        'CF': 'Centre Forwards',
    }
    
    for position in ['GK', 'LB', 'CB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST', 'CF']:
        if position in players_by_position:
            print(f"\n{position_names.get(position, position)}:")
            for player in players_by_position[position]:
                print(f"  • Username: {player['username']}")
                print(f"    Email: {player['email']}")
                print(f"    Password: {player['password']}")
                print()
    
    # Print managers
    print("=" * 80)
    print("👔 MANAGERS")
    print("-" * 80)
    
    for manager in managers:
        print(f"\n• Username: {manager['username']}")
        print(f"  Email: {manager['email']}")
        print(f"  Password: {manager['password']}")
        print(f"  Qualification: {manager['qualification']}")
        print()
    
    # Print scouts
    print("=" * 80)
    print("🔍 SCOUTS")
    print("-" * 80)
    
    for scout in scouts:
        print(f"\n• Username: {scout['username']}")
        print(f"  Email: {scout['email']}")
        print(f"  Password: {scout['password']}")
        print(f"  Organization: {scout['organization']}")
        print()
    
    print("=" * 80)
    print()
    print("📝 QUICK REFERENCE - ALL PASSWORDS: TestPass123!")
    print()
    print("Player usernames follow pattern: <position>_<name>")
    print("Manager usernames follow pattern: manager_<name>")
    print("Scout usernames follow pattern: scout_<name>")
    print()
    print("=" * 80)


if __name__ == '__main__':
    print("\n🚀 Starting user creation process...\n")
    created = create_test_users()
    print_login_credentials(created)
    print("\n✅ All done! You can now log in with any of the accounts above.\n")
