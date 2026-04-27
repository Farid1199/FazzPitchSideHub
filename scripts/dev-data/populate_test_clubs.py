"""
Script to create 15 test clubs for the Find Clubs feature.
Run this script with: python scripts/dev-data/populate_test_clubs.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ClubProfile

# Test clubs data - Birmingham area clubs from Step 1 to Step 7
TEST_CLUBS = [
    # Step 1
    {
        'club_name': 'Solihull Moors',
        'league_level': 'STEP_1',
        'location_postcode': 'B91 3DA',
        'league': 'National League',
        'location': 'Solihull, Birmingham',
        'founded_year': 2007,
        'is_registered': False,
    },
    {
        'club_name': 'Tamworth',
        'league_level': 'STEP_1',
        'location_postcode': 'B79 7NL',
        'league': 'National League',
        'location': 'Tamworth, Staffordshire',
        'founded_year': 1933,
        'is_registered': False,
    },
    # Step 2
    {
        'club_name': 'Rushall Olympic',
        'league_level': 'STEP_2',
        'location_postcode': 'WS4 1LJ',
        'league': 'National League North',
        'location': 'Rushall, Walsall',
        'founded_year': 1893,
        'is_registered': False,
    },
    # Step 3
    {
        'club_name': 'Stourbridge FC',
        'league_level': 'STEP_3',
        'location_postcode': 'DY8 4DF',
        'league': 'Southern League Premier Central',
        'location': 'Stourbridge, West Midlands',
        'founded_year': 1876,
        'is_registered': False,
    },
    {
        'club_name': 'Bromsgrove FC',
        'league_level': 'STEP_3',
        'location_postcode': 'B61 0DR',
        'league': 'Southern League Premier Central',
        'location': 'Bromsgrove, Worcestershire',
        'founded_year': 2009,
        'is_registered': False,
    },
    {
        'club_name': 'Halesowen Town FC',
        'league_level': 'STEP_3',
        'location_postcode': 'B63 3TB',
        'league': 'Southern League Premier Central',
        'location': 'Halesowen, West Midlands',
        'founded_year': 1873,
        'is_registered': False,
    },
    {
        'club_name': 'Alvechurch FC',
        'league_level': 'STEP_3',
        'location_postcode': 'B48 7RS',
        'league': 'Southern League Premier Central',
        'location': 'Alvechurch, Worcestershire',
        'founded_year': 1929,
        'is_registered': False,
    },
    {
        'club_name': 'Hednesford Town FC',
        'league_level': 'STEP_3',
        'location_postcode': 'WS12 2DZ',
        'league': 'Southern League Premier Central',
        'location': 'Hednesford, Staffordshire',
        'founded_year': 1880,
        'is_registered': False,
    },
    # Step 4
    {
        'club_name': 'Sutton Coldfield FC',
        'league_level': 'STEP_4',
        'location_postcode': 'B74 2NH',
        'league': 'Southern League Division One Central',
        'location': 'Sutton Coldfield, Birmingham',
        'founded_year': 1879,
        'is_registered': False,
    },
    {
        'club_name': 'Coleshill Town FC',
        'league_level': 'STEP_4',
        'location_postcode': 'B46 1AE',
        'league': 'Midland Football League Premier',
        'location': 'Coleshill, North Warwickshire',
        'founded_year': 1894,
        'is_registered': False,
    },
    {
        'club_name': 'Lye Town',
        'league_level': 'STEP_4',
        'location_postcode': 'DY9 8RL',
        'league': 'Midland Football League Premier',
        'location': 'Lye, Stourbridge',
        'founded_year': 1930,
        'is_registered': False,
    },
    {
        'club_name': 'Sporting Khalsa',
        'league_level': 'STEP_4',
        'location_postcode': 'B71 4JJ',
        'league': 'Midland Football League Premier',
        'location': 'West Bromwich, West Midlands',
        'founded_year': 1991,
        'is_registered': False,
    },
    # Step 5
    {
        'club_name': 'AFC Wulfrunians',
        'league_level': 'STEP_5',
        'location_postcode': 'WV4 6DT',
        'league': 'Midland Football League Division One',
        'location': 'Wolverhampton, West Midlands',
        'founded_year': 1963,
        'is_registered': False,
    },
    {
        'club_name': 'Romulus',
        'league_level': 'STEP_5',
        'location_postcode': 'B33 0NJ',
        'league': 'Midland Football League Division One',
        'location': 'Castle Bromwich, Birmingham',
        'founded_year': 1979,
        'is_registered': False,
    },
    {
        'club_name': 'Tividale',
        'league_level': 'STEP_5',
        'location_postcode': 'B69 1UG',
        'league': 'Midland Football League Division One',
        'location': 'Tividale, West Midlands',
        'founded_year': 1954,
        'is_registered': False,
    },
    {
        'club_name': 'Wolverhampton Casuals',
        'league_level': 'STEP_5',
        'location_postcode': 'WV11 2PF',
        'league': 'Midland Football League Division One',
        'location': 'Wolverhampton, West Midlands',
        'founded_year': 1953,
        'is_registered': False,
    },
    {
        'club_name': 'Coton Green',
        'league_level': 'STEP_5',
        'location_postcode': 'B79 8JB',
        'league': 'Midland Football League Division One',
        'location': 'Tamworth, Staffordshire',
        'founded_year': 1966,
        'is_registered': False,
    },
    {
        'club_name': 'Dudley Town FC',
        'league_level': 'STEP_5',
        'location_postcode': 'DY2 0PD',
        'league': 'Midland Football League Division One',
        'location': 'Dudley, West Midlands',
        'founded_year': 1888,
        'is_registered': False,
    },
    {
        'club_name': 'AFC Wolverhampton City',
        'league_level': 'STEP_5',
        'location_postcode': 'WV10 7QP',
        'league': 'Midland Football League Division One',
        'location': 'Wolverhampton, West Midlands',
        'founded_year': 2008,
        'is_registered': False,
    },
    # Step 6
    {
        'club_name': 'Cradley Town',
        'league_level': 'STEP_6',
        'location_postcode': 'B63 2TS',
        'league': 'Midland Football League Division Two',
        'location': 'Cradley, West Midlands',
        'founded_year': 1968,
        'is_registered': False,
    },
    {
        'club_name': 'Knowle FC',
        'league_level': 'STEP_6',
        'location_postcode': 'B93 0NT',
        'league': 'Midland Football League Division Two',
        'location': 'Knowle, Solihull',
        'founded_year': 1870,
        'is_registered': False,
    },
    {
        'club_name': 'Smethwick Rangers',
        'league_level': 'STEP_6',
        'location_postcode': 'B67 7AD',
        'league': 'Midland Football League Division Two',
        'location': 'Smethwick, West Midlands',
        'founded_year': 1983,
        'is_registered': False,
    },
    {
        'club_name': 'Bilston Town',
        'league_level': 'STEP_6',
        'location_postcode': 'WV14 6AT',
        'league': 'Midland Football League Division Two',
        'location': 'Bilston, Wolverhampton',
        'founded_year': 1955,
        'is_registered': False,
    },
    {
        'club_name': 'OJM',
        'league_level': 'STEP_6',
        'location_postcode': 'B36 9NU',
        'league': 'Midland Football League Division Two',
        'location': 'Castle Bromwich, Birmingham',
        'founded_year': 1969,
        'is_registered': False,
    },
    {
        'club_name': 'Wednesfield',
        'league_level': 'STEP_6',
        'location_postcode': 'WV11 1TR',
        'league': 'Midland Football League Division Two',
        'location': 'Wednesfield, Wolverhampton',
        'founded_year': 1961,
        'is_registered': False,
    },
    # Step 7
    {
        'club_name': 'Bustleholme',
        'league_level': 'STEP_7',
        'location_postcode': 'B71 3DE',
        'league': 'West Midlands Regional League Premier',
        'location': 'West Bromwich, West Midlands',
        'founded_year': 1974,
        'is_registered': False,
    },
    {
        'club_name': 'Tipton Town',
        'league_level': 'STEP_7',
        'location_postcode': 'DY4 0DT',
        'league': 'West Midlands Regional League Premier',
        'location': 'Tipton, West Midlands',
        'founded_year': 1948,
        'is_registered': False,
    },
    {
        'club_name': 'Pelsall Villa Colts',
        'league_level': 'STEP_7',
        'location_postcode': 'WS3 4AJ',
        'league': 'West Midlands Regional League Premier',
        'location': 'Pelsall, Walsall',
        'founded_year': 1950,
        'is_registered': False,
    },
    {
        'club_name': 'Wrest Nest',
        'league_level': 'STEP_7',
        'location_postcode': 'B71 2EA',
        'league': 'West Midlands Regional League Premier',
        'location': 'West Bromwich, West Midlands',
        'founded_year': 1967,
        'is_registered': False,
    },
    {
        'club_name': 'Wyrley United',
        'league_level': 'STEP_7',
        'location_postcode': 'WS6 6DJ',
        'league': 'West Midlands Regional League Premier',
        'location': 'Great Wyrley, Staffordshire',
        'founded_year': 1972,
        'is_registered': False,
    },
    {
        'club_name': 'Oldbury United',
        'league_level': 'STEP_7',
        'location_postcode': 'B68 8LR',
        'league': 'West Midlands Regional League Premier',
        'location': 'Oldbury, West Midlands',
        'founded_year': 1962,
        'is_registered': False,
    },
    {
        'club_name': 'Dudley Athletic FC',
        'league_level': 'STEP_7',
        'location_postcode': 'DY1 4RN',
        'league': 'West Midlands Regional League Premier',
        'location': 'Dudley, West Midlands',
        'founded_year': 1985,
        'is_registered': False,
    },
    {
        'club_name': 'Stourbridge Standard FC',
        'league_level': 'STEP_7',
        'location_postcode': 'DY8 3XN',
        'league': 'West Midlands Regional League Premier',
        'location': 'Stourbridge, West Midlands',
        'founded_year': 1977,
        'is_registered': False,
    },
    {
        'club_name': 'P S Olympic',
        'league_level': 'STEP_7',
        'location_postcode': 'B68 0DR',
        'league': 'West Midlands Regional League Premier',
        'location': 'Oldbury, West Midlands',
        'founded_year': 1970,
        'is_registered': False,
    },
]

def create_test_clubs():
    """Create all test clubs"""
    
    created_clubs = []
    
    print("=" * 80)
    print("CREATING TEST CLUBS FOR FAZZPITCHSIDEHUB")
    print("=" * 80)
    print()
    
    print("⚽ CREATING CLUBS")
    print("-" * 80)
    
    for club_data in TEST_CLUBS:
        try:
            # Check if club already exists
            if ClubProfile.objects.filter(club_name=club_data['club_name']).exists():
                print(f"⚠️  Club '{club_data['club_name']}' already exists. Skipping...")
                continue
            
            # Create club profile
            club = ClubProfile.objects.create(**club_data)
            
            created_clubs.append({
                'club_name': club_data['club_name'],
                'location': club_data['location'],
                'league_level': club_data['league_level']
            })
            
            print(f"✅ Created club: {club_data['club_name']} ({club_data['location']})")
            
        except Exception as e:
            print(f"❌ Error creating {club_data['club_name']}: {str(e)}")
    
    print()
    print("=" * 80)
    print("✨ CREATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"Total clubs created: {len(created_clubs)}")
    print()
    
    return created_clubs


def print_club_summary(created_clubs):
    """Print summary of created clubs"""
    
    print()
    print("=" * 80)
    print("📋 CLUBS CREATED")
    print("=" * 80)
    print()
    
    # Group by location
    clubs_by_location = {}
    for club in created_clubs:
        location = club['location']
        if location not in clubs_by_location:
            clubs_by_location[location] = []
        clubs_by_location[location].append(club)
    
    for location, clubs in sorted(clubs_by_location.items()):
        print(f"\n📍 {location}:")
        for club in clubs:
            level_display = dict(ClubProfile.LEAGUE_LEVEL_CHOICES).get(club['league_level'], club['league_level'])
            print(f"  • {club['club_name']} - {level_display}")
    
    print()
    print("=" * 80)
    print()
    print("🎯 You can now search for these clubs at: http://127.0.0.1:8000/search-clubs/")
    print()
    print("=" * 80)


if __name__ == '__main__':
    print("\n🚀 Starting club creation process...\n")
    created = create_test_clubs()
    print_club_summary(created)
    print("\n✅ All done! Visit the Find Clubs page to see the results.\n")
