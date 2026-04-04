"""
Script to sync/pull database from Railway to local PostgreSQL
"""
import os
import sys
import django

print("=" * 70)
print("  SYNCING RAILWAY DATABASE TO LOCAL")
print("=" * 70)
print()

# Step 1: Export data from Railway
print("Step 1: Exporting data from Railway...")
os.environ['DATABASE_URL'] = 'postgresql://postgres:CmAfDwLtIMtOYscAjsvOPYWntlastOdP@maglev.proxy.rlwy.net:13709/railway'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')

# Clear any existing Django setup
if 'django' in sys.modules:
    del sys.modules['django']
    for key in list(sys.modules.keys()):
        if key.startswith('django.'):
            del sys.modules[key]

django.setup()

from django.core.management import call_command

# Export Railway data to JSON
print("  → Dumping Railway data to railway_dump.json...")
with open('railway_dump.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', 
                 '--natural-foreign', 
                 '--natural-primary',
                 '--indent', '2',
                 '--exclude', 'contenttypes',
                 '--exclude', 'auth.permission',
                 '--exclude', 'admin.logentry',
                 '--exclude', 'sessions.session',
                 stdout=f)

print("  ✓ Railway data exported to railway_dump.json")
print()

# Step 2: Reload Django with local database
print("Step 2: Switching to local PostgreSQL...")

# Remove DATABASE_URL to use local DB config
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

# Force Django to reload
from importlib import reload
from django import conf
from django.db import connection
connection.close()

# Reload settings
if 'smartneighbour_api.settings' in sys.modules:
    del sys.modules['smartneighbour_api.settings']

# Clear Django apps
if hasattr(django, 'apps'):
    django.apps.apps.app_configs = {}
    django.apps.apps.ready = False

# Re-setup Django
django.setup()

print("  ✓ Connected to local PostgreSQL")
print()

# Step 3: Load data to local
print("Step 3: Loading data to local PostgreSQL...")
print("  → Flushing existing local data (except superuser)...")

try:
    # Clear existing data
    from core.models import User, Resident, Feedback, Announcement, SecuritySchedule, SecurityPersonnel, RW, RT
    
    SecuritySchedule.objects.all().delete()
    SecurityPersonnel.objects.all().delete()
    Announcement.objects.all().delete()
    Feedback.objects.all().delete()
    Resident.objects.all().delete()
    RT.objects.all().delete()
    RW.objects.all().delete()
    User.objects.all().delete()
    
    print("  ✓ Local data cleared")
    print()
    
    print("  → Loading Railway data to local...")
    call_command('loaddata', 'railway_dump.json')
    
    print("  ✓ Data loaded successfully!")
    print()
    
    # Verify
    from core.models import User, Resident, Feedback, Announcement, SecuritySchedule
    
    print("=" * 70)
    print("  VERIFICATION")
    print("=" * 70)
    print(f"  ✓ Users: {User.objects.count()}")
    print(f"  ✓ Residents: {Resident.objects.count()}")
    print(f"  ✓ Feedbacks: {Feedback.objects.count()}")
    print(f"  ✓ Announcements: {Announcement.objects.count()}")
    print(f"  ✓ Security Schedules: {SecuritySchedule.objects.count()}")
    print()
    print("=" * 70)
    print("  ✓ SYNC COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    print()
    print("Note: You may need to run migrations first:")
    print("  python manage.py migrate")
    sys.exit(1)
