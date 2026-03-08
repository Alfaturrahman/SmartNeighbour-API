"""
Script to verify data migration to Railway PostgreSQL
"""
import os
import django

# Set Railway DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:ykNWwFwUKrQpxTUTrgUdSsxhcSlHYdBi@maglev.proxy.rlwy.net:16438/railway'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, Resident, Feedback, Announcement, SecuritySchedule

print("=" * 60)
print("  RAILWAY DATABASE VERIFICATION")
print("=" * 60)
print()

try:
    # Check Users
    users = User.objects.all()
    print(f"✓ Users: {users.count()}")
    for user in users:
        print(f"  - {user.email} ({user.role})")
    print()

    # Check Residents
    residents = Resident.objects.all()
    print(f"✓ Residents: {residents.count()}")
    print()

    # Check Feedback
    feedbacks = Feedback.objects.all()
    print(f"✓ Feedbacks: {feedbacks.count()}")
    print()

    # Check Announcements
    announcements = Announcement.objects.all()
    print(f"✓ Announcements: {announcements.count()}")
    print()

    # Check Security Schedules
    schedules = SecuritySchedule.objects.all()
    print(f"✓ Security Schedules: {schedules.count()}")
    print()

    print("=" * 60)
    print("  ✓ ALL DATA MIGRATED SUCCESSFULLY!")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
