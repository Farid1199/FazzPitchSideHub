# FazzPitchSideHub

Simple setup instructions for running this project locally.

## What this project uses

- Python
- Django 5.2
- SQLite database (`db.sqlite3`)

## Quick Start (Windows)

Open PowerShell in the project folder and run these commands:

```powershell
cd C:\Users\Farid\FazzPitchSideHub
\env\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## If the virtual environment is not working

Create a new one and install the packages again:

```powershell
cd C:\Users\Farid\FazzPitchSideHub
python -m venv env
\env\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment variables

This project can run in development without a full `.env` file, but it is better to add one.

Create a `.env` file in the project root with this content:

```env
DJANGO_SECRET_KEY=change-this-to-your-own-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

## Useful commands

Run migrations:

```powershell
python manage.py migrate
```

Create an admin user:

```powershell
python manage.py createsuperuser
```

Run tests:

```powershell
python manage.py test
```

Run utility scripts (now organized under scripts/):

```powershell
# Dev data setup
python scripts/dev-data/populate_test_users.py
python scripts/dev-data/populate_test_clubs.py

# Maintenance helpers
python scripts/maintenance/demo_club_types.py
python scripts/maintenance/check_users.py

# Manual script-based checks
python scripts/manual-tests/test_search.py
```

Open the Django admin:

```text
http://127.0.0.1:8000/admin/
```

## Project structure

The repository root now keeps only core app files. Utility scripts are grouped by purpose:

- scripts/dev-data/: test data generation and local seed helpers
- scripts/maintenance/: maintenance and data-fix scripts
- scripts/manual-tests/: script-style checks (separate from Django test suite)
- scripts/debug/: temporary debugging scripts

## Common problem

If PowerShell blocks the activate script, run this once in PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again:

```powershell
\env\Scripts\Activate.ps1
```