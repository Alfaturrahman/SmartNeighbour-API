import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')
django.setup()

from core.models import User, Resident, RT, RW, SecuritySchedule
from datetime import date

# Check warga user
warga = User.objects.filter(email='warga@test.com').first()
print('=== WARGA USER ===')
print(f'User: {warga}')
print(f'Email: {warga.email if warga else None}')
print(f'Role: {warga.role if warga else None}')
print()

# Check resident profile
print('=== RESIDENT PROFILE ===')
if warga:
    try:
        resident = warga.resident_profile
        print(f'Resident: {resident}')
        print(f'Resident RT: {resident.rt}')
        print(f'Resident RT ID: {resident.rt.id if resident.rt else None}')
        print(f'Resident RW: {resident.rt.rw if resident.rt else None}')
        print(f'Resident RW ID: {resident.rt.rw.id if resident.rt and resident.rt else None}')
    except User.resident_profile.RelatedObjectDoesNotExist:
        print('NO RESIDENT PROFILE FOUND!')
        print('Checking all residents...')
        all_residents = Resident.objects.all()
        print(f'Total residents in system: {all_residents.count()}')
        for res in all_residents:
            print(f'  - {res.name} ({res.email}) - User: {res.user} - RT: {res.rt}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
print()

# Check security schedules for ALL RWs
print('=== ALL RWs and SCHEDULES ===')
all_rws = RW.objects.all()
for rw in all_rws:
    print(f'\nRW: {rw.name} (ID: {rw.id})')
    schedules = SecuritySchedule.objects.filter(rw=rw, status='aktif')
    print(f'  Active schedules: {schedules.count()}')
    
    today = date.today()
    today_schedules = schedules.filter(start_date__lte=today, end_date__gte=today)
    print(f'  Schedules active today ({today}): {today_schedules.count()}')
    
    if today_schedules.count() > 0:
        for s in today_schedules[:3]:
            print(f'    - {s.name} | {s.shift} | {s.start_date} to {s.end_date}')
