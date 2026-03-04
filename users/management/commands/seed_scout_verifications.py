"""
Management command: seed_scout_verifications
Creates three test scout users with ScoutVerification records at different states.

Usage:
    python manage.py seed_scout_verifications
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

from users.models import User, ScoutProfile, ScoutVerification, Notification

DUMMY_CERT = ContentFile(b'%PDF-1.4 dummy test certificate', name='test_cert.pdf')


class Command(BaseCommand):
    help = 'Seed 3 test scout users with verification records (pending / approved / rejected)'

    TEST_SCOUTS = [
        {
            'username': 'scout_pending',
            'email': 'scout_pending@fazz.test',
            'password': 'FazzTest2024!',
            'first_name': 'Pending',
            'last_name': 'Scout',
            'organization': 'Local Grassroots FC',
            'region': 'West Midlands',
            'verification': {
                'requested_tier': 'TIER1',
                'qualification_body': 'FA',
                'qualification_level': 'LEVEL1',
                'fa_fan_number': '99000001',
                'status': 'PENDING',
            },
        },
        {
            'username': 'scout_verified',
            'email': 'scout_verified@fazz.test',
            'password': 'FazzTest2024!',
            'first_name': 'Verified',
            'last_name': 'Scout',
            'organization': 'Academy Scouting Network',
            'region': 'London',
            'verification': {
                'requested_tier': 'TIER2',
                'qualification_body': 'FA',
                'qualification_level': 'LEVEL2',
                'fa_fan_number': '99000002',
                'status': 'APPROVED',
                'awarded_tier': 'TIER2',
            },
        },
        {
            'username': 'scout_rejected',
            'email': 'scout_rejected@fazz.test',
            'password': 'FazzTest2024!',
            'first_name': 'Rejected',
            'last_name': 'Scout',
            'organization': 'Independent Scouting',
            'region': 'Manchester',
            'verification': {
                'requested_tier': 'TIER3',
                'qualification_body': 'UEFA',
                'qualification_level': 'LEVEL3',
                'status': 'REJECTED',
                'rejection_reason': 'The certificate uploaded was not legible. Please resubmit a clearer scan.',
            },
        },
    ]

    def handle(self, *args, **options):
        for data in self.TEST_SCOUTS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'SCOUT',
                },
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  Created user: {user.username}'))
            else:
                self.stdout.write(f'  User already exists: {user.username}')

            # Ensure ScoutProfile
            scout_profile, _ = ScoutProfile.objects.get_or_create(
                user=user,
                defaults={
                    'organization': data.get('organization', ''),
                    'region': data.get('region', ''),
                },
            )

            v_data = data['verification']
            verification, v_created = ScoutVerification.objects.get_or_create(
                scout=scout_profile,
                defaults={
                    'requested_tier': v_data.get('requested_tier', 'TIER1'),
                    'qualification_body': v_data.get('qualification_body', 'FA'),
                    'qualification_level': v_data.get('qualification_level', 'LEVEL1'),
                    'fa_fan_number': v_data.get('fa_fan_number', ''),
                    'certificate_file': ContentFile(
                        b'%PDF-1.4 test certificate placeholder',
                        name=f'{data["username"]}_cert.pdf',
                    ),
                    'status': v_data.get('status', 'PENDING'),
                    'awarded_tier': v_data.get('awarded_tier', ''),
                    'submitted_at': timezone.now(),
                    'rejection_reason': v_data.get('rejection_reason', ''),
                },
            )

            if v_created:
                # If approved, update the ScoutProfile too
                if v_data['status'] == 'APPROVED':
                    scout_profile.scout_verified = True
                    scout_profile.verification_tier = v_data.get('awarded_tier', '')
                    scout_profile.save()
                    verification.reviewed_at = timezone.now()
                    verification.save()
                    Notification.objects.create(
                        user=user,
                        message=f'Congratulations! Your scout verification has been approved at '
                                f'{verification.get_awarded_tier_display()} level.',
                    )

                elif v_data['status'] == 'REJECTED':
                    verification.reviewed_at = timezone.now()
                    verification.save()
                    Notification.objects.create(
                        user=user,
                        message='Your scout verification application has been rejected. '
                                'Please review the rejection reason and resubmit.',
                    )

                self.stdout.write(self.style.SUCCESS(
                    f'    -> ScoutVerification ({v_data["status"]}) created'
                ))
            else:
                self.stdout.write(f'    -> ScoutVerification already exists')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Test Scout Credentials ==='))
        for data in self.TEST_SCOUTS:
            self.stdout.write(
                f'  {data["username"]} / {data["password"]}  '
                f'({data["verification"]["status"]})'
            )
        self.stdout.write('')
