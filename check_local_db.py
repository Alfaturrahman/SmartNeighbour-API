import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, RW, RT, Resident, SecurityPersonnel, SecuritySchedule, Feedback, Announcement

print("\n" + "=" * 70)
print("LOCAL DATABASE (SQLite) CONTENT CHECK")
print("=" * 70)

print("\n1. OVERALL STATISTICS")
print("-" * 70)
print(f"Users: {User.objects.count()}")
print(f"RW: {RW.objects.count()}")
print(f"RT: {RT.objects.count()}")
print(f"Residents: {Resident.objects.count()}")
print(f"Security Personnel: {SecurityPersonnel.objects.count()}")
print(f"Security Schedules: {SecuritySchedule.objects.count()}")
print(f"Feedback: {Feedback.objects.count()}")
print(f"Announcements: {Announcement.objects.count()}")

print("\n2. SECURITY SCHEDULES (Active)")
print("-" * 70)
schedules = SecuritySchedule.objects.filter(status='aktif')
print(f"Total active schedules: {schedules.count()}")
if schedules.exists():
    for s in schedules[:5]:
        print(f"  - {s.name} | {s.shift} | {s.start_date} to {s.end_date}")
else:
    print("  No active schedules")

print("\n3. SECURITY PERSONNEL")
print("-" * 70)
personnel = SecurityPersonnel.objects.all()
print(f"Total personnel: {personnel.count()}")
if personnel.exists():
    for p in personnel[:5]:
        print(f"  - {p.name} | {p.phone} | {p.status}")

print("\n4. FEEDBACK")
print("-" * 70)
feedback = Feedback.objects.all()
print(f"Total feedback: {feedback.count()}")
with_reply = Feedback.objects.filter(reply__isnull=False).count()
print(f"With reply: {with_reply}")

if feedback.exists():
    print("\nSample feedback:")
    for f in feedback[:3]:
        status = "✓" if f.reply else "○"
        print(f"  {status} '{f.title}' by {f.author}")
        if f.reply:
            print(f"      → Replied by {f.replied_by}")

print("\n5. ANNOUNCEMENTS")
print("-" * 70)
announcements = Announcement.objects.all()
print(f"Total announcements: {announcements.count()}")
if announcements.exists():
    for a in announcements[:3]:
        print(f"  - [{a.priority}] {a.title} by {a.author}")

print("\n6. RESIDENTS")
print("-" * 70)
residents = Resident.objects.all()
print(f"Total residents: {residents.count()}")
if residents.exists():
    for r in residents[:3]:
        print(f"  - {r.name} ({r.email}) - RT: {r.rt}")

print("\n" + "=" * 70)
print("COMPARISON: LOCAL vs PRODUCTION")
print("=" * 70)
print("\nPRODUCTION currently has:")
print("  - Security Schedules: 0")
print("  - Feedback: 0")
print("  - Announcements: 0")
print("  - Residents: 3 (warga profiles created)")
print("\nLOCAL has:")
print(f"  - Security Schedules: {SecuritySchedule.objects.count()}")
print(f"  - Feedback: {Feedback.objects.count()}")
print(f"  - Announcements: {Announcement.objects.count()}")
print(f"  - Residents: {Resident.objects.count()}")

print("\n" + "=" * 70)
if SecuritySchedule.objects.count() > 0 or Feedback.objects.count() > 0:
    print("✓ LOCAL has useful data that can be imported")
    print("\nWould you like to import this data to production?")
else:
    print("○ LOCAL database is mostly empty")
    print("\nRecommendation: Start fresh in production")
print("=" * 70 + "\n")
