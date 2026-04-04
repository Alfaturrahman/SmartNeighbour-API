"""
Script to create resident profiles for warga users who don't have one yet.
Run this after deploying to Railway to ensure all warga users can access the system.

Usage:
    railway run python fix_warga_residents.py
    
Or in Django shell:
    python manage.py shell < fix_warga_residents.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, Resident, RT

def fix_warga_residents():
    """Create resident profiles for warga users without one"""
    
    print("=" * 60)
    print("FIXING WARGA RESIDENT PROFILES")
    print("=" * 60)
    
    # Get all warga users
    warga_users = User.objects.filter(role='warga', is_active=True)
    print(f"\nTotal warga users in system: {warga_users.count()}")
    
    # Get default RT (first one) for users without specific RT
    default_rt = RT.objects.first()
    if not default_rt:
        print("ERROR: No RT found in system! Create RW and RT first.")
        return
    
    print(f"Default RT for new residents: {default_rt.name} (under {default_rt.rw.name})")
    
    # Check each warga user
    created_count = 0
    already_exists_count = 0
    
    for user in warga_users:
        try:
            # Check if resident profile exists
            resident = user.resident_profile
            print(f"✓ {user.name} ({user.email}) - Already has resident profile")
            already_exists_count += 1
            
        except Resident.DoesNotExist:
            # Create resident profile
            print(f"✗ {user.name} ({user.email}) - Creating resident profile...")
            
            resident = Resident.objects.create(
                user=user,
                rt=default_rt,
                name=user.name,
                email=user.email,
                phone='000000000000',  # Default phone
                address='Alamat belum diisi',  # Default address
                status='aktif',
                ktp=None,  # To be filled by RT
                kk=None,  # To be filled by RT
                jumlah_keluarga=1,
                kepala_keluarga=user.name
            )
            
            print(f"  ✓ Created: {resident.name} linked to {resident.rt.name}")
            created_count += 1
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total warga users: {warga_users.count()}")
    print(f"Already had resident profile: {already_exists_count}")
    print(f"Newly created profiles: {created_count}")
    print("\n✓ All warga users now have resident profiles!")
    print("\nNext steps:")
    print("1. Ask RT to update resident details (phone, address, KTP, KK)")
    print("2. Test login with warga accounts")
    print("3. Verify they can see jadwal keamanan and feedback")
    print("=" * 60)

if __name__ == '__main__':
    fix_warga_residents()
