"""
Check RT data for debugging
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')

import django
django.setup()

from core.models import User, RT, RW

print("=" * 60)
print("  DEBUG: RT Users and Profiles")
print("=" * 60)
print()

# Get RT users
rt_users = User.objects.filter(role='rt')
print(f"Total RT users: {rt_users.count()}")
print()

for user in rt_users:
    print(f"Email: {user.email}")
    print(f"  Role: {user.role}")
    
    # Check if has RT profile
    try:
        rt_profile = RT.objects.get(user=user)
        print(f"  ✓ Has RT Profile:")
        print(f"    - RT ID: {rt_profile.id}")
        print(f"    - RT Name: {rt_profile.name}")
        print(f"    - RT Area: {rt_profile.area or 'N/A'}")
        print(f"    - RW: {rt_profile.rw.name if rt_profile.rw else 'N/A'}")
    except RT.DoesNotExist:
        print(f"  ✗ NO RT Profile!")
    
    print()

print("=" * 60)
print("  All RT Profiles")
print("=" * 60)
print()

all_rts = RT.objects.all()
print(f"Total RT profiles: {all_rts.count()}")
print()

for rt in all_rts:
    print(f"RT: {rt.name}")
    print(f"  User Email: {rt.user.email}")
    print(f"  RW: {rt.rw.name if rt.rw else 'NO RW!'}")
    print()

print("=" * 60)
print("  All RW Profiles")
print("=" * 60)
print()

all_rws = RW.objects.all()
print(f"Total RW profiles: {all_rws.count()}")
print()

for rw in all_rws:
    print(f"RW: {rw.name}")
    print(f"  User Email: {rw.user.email}")
    print()
