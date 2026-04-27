import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("Creating migrations...")
call_command('makemigrations')

print("\nApplying migrations...")
call_command('migrate')

print("\n✅ Migrations complete!")
