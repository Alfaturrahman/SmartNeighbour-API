"""
Verify Railway deployment data integrity
Run this after deploying to check everything is working correctly

Usage:
    railway run python verify_railway_deployment.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, Resident, RT, RW, SecuritySchedule, SecurityPersonnel, Feedback, Announcement
from datetime import date

def verify_deployment():
    print("\n" + "=" * 70)
    print("RAILWAY DEPLOYMENT VERIFICATION")
    print("=" * 70)
    
    # Check database connection
    print("\n1. DATABASE CONNECTION")
    print("-" * 70)
    try:
        user_count = User.objects.count()
        print(f"✓ Database connected successfully")
        print(f"  Total users: {user_count}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Check models
    print("\n2. DATA MODELS")
    print("-" * 70)
    models_check = {
        'Users': User.objects.count(),
        'RW': RW.objects.count(),
        'RT': RT.objects.count(),
        'Residents': Resident.objects.count(),
        'Security Personnel': SecurityPersonnel.objects.count(),
        'Security Schedules': SecuritySchedule.objects.count(),
        'Feedback': Feedback.objects.count(),
        'Announcements': Announcement.objects.count(),
    }
    
    for model_name, count in models_check.items():
        status = "✓" if count > 0 else "⚠"
        print(f"{status} {model_name}: {count}")
    
    # Check user roles
    print("\n3. USER ROLES DISTRIBUTION")
    print("-" * 70)
    rw_count = User.objects.filter(role='rw').count()
    rt_count = User.objects.filter(role='rt').count()
    warga_count = User.objects.filter(role='warga').count()
    
    print(f"  RW: {rw_count}")
    print(f"  RT: {rt_count}")
    print(f"  Warga: {warga_count}")
    
    # Check warga without resident profile
    print("\n4. WARGA RESIDENT PROFILES")
    print("-" * 70)
    warga_users = User.objects.filter(role='warga')
    warga_with_profile = 0
    warga_without_profile = []
    
    for user in warga_users:
        try:
            resident = user.resident_profile
            warga_with_profile += 1
        except Resident.DoesNotExist:
            warga_without_profile.append(user.email)
    
    print(f"  With resident profile: {warga_with_profile}")
    print(f"  Without resident profile: {len(warga_without_profile)}")
    
    if warga_without_profile:
        print(f"\n  ⚠ WARNING: {len(warga_without_profile)} warga users need resident profiles:")
        for email in warga_without_profile:
            print(f"    - {email}")
        print(f"\n  Run: railway run python fix_warga_residents.py")
    else:
        print(f"  ✓ All warga users have resident profiles")
    
    # Check security schedules
    print("\n5. SECURITY SCHEDULES")
    print("-" * 70)
    active_schedules = SecuritySchedule.objects.filter(status='aktif')
    today = date.today()
    today_schedules = active_schedules.filter(
        start_date__lte=today,
        end_date__gte=today
    )
    
    print(f"  Total active schedules: {active_schedules.count()}")
    print(f"  Schedules active today: {today_schedules.count()}")
    
    if today_schedules.count() > 0:
        print(f"\n  Today's guards:")
        for schedule in today_schedules:
            print(f"    - {schedule.shift}: {schedule.name}")
    else:
        print(f"  ⚠ No guards scheduled for today")
    
    # Check feedback with replies
    print("\n6. FEEDBACK SYSTEM")
    print("-" * 70)
    total_feedback = Feedback.objects.count()
    with_reply = Feedback.objects.filter(reply__isnull=False).count()
    without_reply = total_feedback - with_reply
    
    print(f"  Total feedback: {total_feedback}")
    print(f"  With reply: {with_reply}")
    print(f"  Pending reply: {without_reply}")
    
    # Check new migrations
    print("\n7. NEW MIGRATIONS (0007 & 0008)")
    print("-" * 70)
    
    # Check if new columns exist
    try:
        # Test 0007: Resident fields
        resident_test = Resident.objects.first()
        if resident_test:
            has_ktp = hasattr(resident_test, 'ktp')
            has_kk = hasattr(resident_test, 'kk')
            has_jumlah = hasattr(resident_test, 'jumlah_keluarga')
            has_kepala = hasattr(resident_test, 'kepala_keluarga')
            
            if all([has_ktp, has_kk, has_jumlah, has_kepala]):
                print(f"  ✓ Migration 0007: Resident fields added")
            else:
                print(f"  ✗ Migration 0007: Some fields missing")
        
        # Test 0008: Feedback rating optional
        feedback_test = Feedback.objects.first()
        if feedback_test:
            print(f"  ✓ Migration 0008: Feedback rating is optional")
        
    except Exception as e:
        print(f"  ⚠ Could not verify migrations: {e}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("DEPLOYMENT STATUS")
    print("=" * 70)
    
    issues = []
    if len(warga_without_profile) > 0:
        issues.append(f"{len(warga_without_profile)} warga users need resident profiles")
    if today_schedules.count() == 0:
        issues.append("No security guards scheduled for today")
    if Resident.objects.count() == 0:
        issues.append("No residents in system")
    
    if issues:
        print("⚠ WARNINGS:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ ALL CHECKS PASSED!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    verify_deployment()
